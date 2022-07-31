# -*- coding: utf8 -*-
# author: ty
import functools
import threading
import uuid
from datetime import datetime

from bson import ObjectId
from pymongo.collection import Collection, ReturnDocument
from pymongo.database import Database
from redis.lock import Lock


class TransactionException(Exception):
    def __init__(self, state, msg=u'', e=None):
        self.state = state
        self.msg = msg
        self.e = e

    def get_state(self):
        return self.state

    def get_msg(self):
        return self.msg

    def get_info(self):
        return self.e


conn_db = None
col_transaction = None
col_backup = None
col_backup_name = 'transaction_backup_date'
redis_lock = None
orig_get_item = None
new_get_item = lambda x, n: CollectionExt(x, n)
trans_lock_name = 'mongo_transaction'


# 利用redis 分布式锁 + 二段提交 实现 串行化非嵌套的事务
def SupportTransaction(conn_db_session, rs_lock):
    global conn_db, col_transaction, col_backup, col_backup_name, redis_lock, orig_get_item
    conn_db = conn_db_session
    redis_lock = rs_lock
    col_transaction = conn_db['transaction']
    col_backup = conn_db[col_backup_name]
    orig_get_item = Database.__getitem__
    Database.__getitem__ = new_get_item


g_transaction_obj = threading.local()


class CollectionExt(Collection):
    def find_one_and_update(self, filter, update,
                            projection=None, sort=None, upsert=False,
                            return_document=ReturnDocument.BEFORE,
                            array_filters=None, session=None, **kwargs):
        global g_transaction_obj
        if hasattr(g_transaction_obj, 'id') and g_transaction_obj.id:
            backup_data(self, filter, False, **kwargs)
            if upsert:
                backup_data(self, filter, False, **kwargs)
                result = super(CollectionExt, self).find_one_and_update(filter, update,
                                                                        projection, sort, upsert,
                                                                        return_document,
                                                                        array_filters, session, **kwargs)
                if result is None:
                    _obj = super(CollectionExt, self).find_one(filter, {'_id': 1})
                    insert_ids = [_obj['_id']]
                    backup_data(self, filter, is_update=False, insert_ids=insert_ids)
                return result
        return super(CollectionExt, self).find_one_and_update(filter, update,
                                                              projection, sort, upsert,
                                                              return_document,
                                                              array_filters, session, **kwargs)

    def find_and_modify(self, query={}, update=None,
                        upsert=False, sort=None, full_response=False,
                        manipulate=False, **kwargs):
        global g_transaction_obj
        if hasattr(g_transaction_obj, 'id') and g_transaction_obj.id:
            backup_data(self, query, False, **kwargs)
            if upsert:
                backup_data(self, query, multi=False)
                result = super(CollectionExt, self).find_and_modify(query, update,
                                                                    upsert, sort, True,
                                                                    manipulate, **kwargs)
                if result['lastErrorObject'].has_key('upserted'):
                    insert_ids = [result['lastErrorObject']['upserted']]
                    backup_data(self, None, is_update=False, insert_ids=insert_ids)
                if full_response:
                    return result
                else:
                    return result['value']
        return super(CollectionExt, self).find_and_modify(query, update,
                                                          upsert, sort, full_response,
                                                          manipulate, **kwargs)

    def find_one_and_replace(self, filter, replacement,
                             projection=None, sort=None, upsert=False,
                             return_document=ReturnDocument.BEFORE,
                             session=None, **kwargs):
        global g_transaction_obj
        if hasattr(g_transaction_obj, 'id') and g_transaction_obj.id:
            backup_data(self, filter, False, **kwargs)
            if upsert:
                result = super(CollectionExt, self).find_one_and_replace(filter, replacement,
                                                                         projection, sort, upsert,
                                                                         return_document,
                                                                         session, **kwargs)
                if result is None:
                    _obj = super(CollectionExt, self).find_one(filter, {'_id': 1})
                    insert_ids = [_obj['_id']]
                    backup_data(self, filter, is_update=False, insert_ids=insert_ids)
                return result

        return super(CollectionExt, self).find_one_and_replace(filter, replacement,
                                                               projection, sort, upsert,
                                                               return_document,
                                                               session, **kwargs)

    def update(self, spec, document, upsert=False, manipulate=False,
               multi=False, check_keys=True, **kwargs):
        global g_transaction_obj
        if hasattr(g_transaction_obj, 'id') and g_transaction_obj.id:
            backup_data(self, spec, multi, **kwargs)

            if upsert:
                result = super(CollectionExt, self).update(spec, document, upsert, manipulate,
                                                           multi, check_keys, **kwargs)
                if result.get('upserted', None) is not None:
                    insert_ids = [result['upserted']]
                    backup_data(self, filter, multi=multi, is_update=False, insert_ids=insert_ids)
                return result
        return super(CollectionExt, self).update(spec, document, upsert, manipulate,
                                                 multi, check_keys, **kwargs)

    def update_one(self, filter, update, upsert=False,
                   bypass_document_validation=False,
                   collation=None, array_filters=None, session=None, **kwargs):
        global g_transaction_obj
        if hasattr(g_transaction_obj, 'id') and g_transaction_obj.id:
            backup_data(self, filter, False, **kwargs)
            if upsert:
                result = super(CollectionExt, self).update_one(filter, update, upsert,
                                                               bypass_document_validation,
                                                               collation, array_filters, session)
                if result.upserted_id:
                    insert_ids = [result.upserted_id]
                    backup_data(self, filter, is_update=False, insert_ids=insert_ids)
                return result
        return super(CollectionExt, self).update_one(filter, update, upsert,
                                                     bypass_document_validation,
                                                     collation, array_filters, session)

    def update_many(self, filter, update, upsert=False, array_filters=None,
                    bypass_document_validation=False, collation=None,
                    session=None, **kwargs):
        global g_transaction_obj
        if hasattr(g_transaction_obj, 'id') and g_transaction_obj.id:
            backup_data(self, filter, multi=True, **kwargs)
            if upsert:
                result = super(CollectionExt, self).update_many(filter, update, upsert, array_filters,
                                                                bypass_document_validation, collation,
                                                                session)
                if result.upserted_id:
                    insert_ids = [result.upserted_id]
                    backup_data(self, filter, multi=True, is_update=False, insert_ids=insert_ids)
                return result

        return super(CollectionExt, self).update_many(filter, update, upsert, array_filters,
                                                      bypass_document_validation, collation,
                                                      session)

    # ----------------------------------

    def insert(self, doc_or_docs, manipulate=True,
               check_keys=True, continue_on_error=False, **kwargs):
        global g_transaction_obj
        result = super(CollectionExt, self).insert(doc_or_docs, manipulate,
                                                   check_keys, continue_on_error)
        if result and hasattr(g_transaction_obj, 'id') and g_transaction_obj.id:
            insert_ids = result
            if not isinstance(result, (list, tuple)):
                insert_ids = [result]
            backup_data(self, doc_or_docs, is_update=False, insert_ids=insert_ids)
        return result

    def insert_one(self, document, bypass_document_validation=False,
                   session=None):
        global g_transaction_obj
        result = super(CollectionExt, self).insert_one(document, bypass_document_validation,
                                                       session)
        if result and result.inserted_id and hasattr(g_transaction_obj, 'id') and g_transaction_obj.id:
            backup_data(self, document, is_update=False, insert_ids=[result.inserted_id])
        return result

    def insert_many(self, documents, ordered=True,
                    bypass_document_validation=False, session=None):
        global g_transaction_obj
        result = super(CollectionExt, self).insert_many(documents, ordered,
                                                        bypass_document_validation, session)
        if result and result.inserted_ids and hasattr(g_transaction_obj, 'id') and g_transaction_obj.id:
            backup_data(self, {}, multi=True, is_update=False, insert_ids=result.inserted_ids)
        return result

    def bulk_write(self, requests, ordered=True,
                   bypass_document_validation=False, session=None):
        global g_transaction_obj
        if hasattr(g_transaction_obj, 'id') and g_transaction_obj.id:
            raise TransactionException(2, u'事务不支持批量写入')
        return super(CollectionExt, self).bulk_write(requests, ordered,
                                                     bypass_document_validation, session)

    # -----------------------------------------------------------------------------------------
    def remove(self, spec_or_id=None, multi=True, **kwargs):
        global g_transaction_obj
        if hasattr(g_transaction_obj, 'id') and g_transaction_obj.id:
            backup_data(self, spec_or_id, multi, is_remove=True)
        return super(CollectionExt, self).remove(spec_or_id, multi, **kwargs)

    def delete_one(self, filter, collation=None, session=None):
        global g_transaction_obj
        if hasattr(g_transaction_obj, 'id') and g_transaction_obj.id:
            backup_data(self, filter, False, is_remove=True)
        return super(CollectionExt, self).delete_one(filter, collation, session)

    def delete_many(self, filter, collation=None, session=None):
        global g_transaction_obj
        if hasattr(g_transaction_obj, 'id') and g_transaction_obj.id:
            backup_data(self, filter, True, is_remove=True)
        return super(CollectionExt, self).delete_many(filter, collation, session)

    def find_one_and_delete(self, filter,
                            projection=None, sort=None, session=None, **kwargs):
        global g_transaction_obj
        if hasattr(g_transaction_obj, 'id') and g_transaction_obj.id:
            backup_data(self, filter, False, is_remove=True)
        return super(CollectionExt, self).find_one_and_delete(filter, projection, sort, session, **kwargs)


def init_transaction():
    global g_transaction_obj
    try:
        if g_transaction_obj.id != None:
            raise TransactionException(0, '不支持事务嵌套')
    except AttributeError:
        g_transaction_obj.id = None
    transaction_data = {
        'records': [],
        'state': 'initial',
        'lastModified': datetime.now()
    }
    result = col_transaction.insert_one(transaction_data)
    if not result.inserted_id:
        raise TransactionException(0)
    g_transaction_obj.id = result.inserted_id


def begin_transaction():
    global g_transaction_obj
    t_id = g_transaction_obj.id
    col_transaction.update_one({'_id': t_id, 'state': 'initial'},
                               {'$set': {'state': 'pending', 'lastModified': datetime.now()}})


def end_transaction():
    global g_transaction_obj
    t_id = g_transaction_obj.id
    col_transaction.update_one({'_id': t_id, 'state': 'pending'},
                               {'$set': {'state': 'applied', 'lastModified': datetime.now()}})


def release_transaction():
    global g_transaction_obj
    g_transaction_obj.id = None


def close_transaction(t_id):
    t_obj = col_transaction.find_one_and_update({'_id': t_id, 'state': {'$in': ['applied']}},
                                                {'$set': {'state': 'done', 'lastModified': datetime.now()}},
                                                ReturnDocument=ReturnDocument.AFTER)
    for record in t_obj['records']:
        trans_name = record['trans_name']
        col_backup.remove({'trans_name': trans_name})

    clear_trans_data(t_id)


def rollback_close_transaction(t_id):
    t_obj = col_transaction.find_one_and_update({'_id': t_id, 'state': {'$in': ['canceled']}},
                                                {'$set': {'lastModified': datetime.now()}},
                                                ReturnDocument=ReturnDocument.AFTER)
    for record in t_obj['records']:
        trans_name = record['trans_name']
        col_backup.remove({'trans_name': trans_name})

    clear_trans_data(t_id)


def get_transaction_id():
    global g_transaction_obj
    return g_transaction_obj.id


def get_transaction_state():
    global g_transaction_obj
    t_id = g_transaction_obj.id
    if t_id:
        return col_transaction.find_one({'_id': t_id}, {'state': 1})['state']
    return ''


def backup_data(collection, query, multi=False, is_update=True, is_remove=False, insert_ids=[], **kwargs):
    global g_transaction_obj, col_backup_name
    t_id = g_transaction_obj.id
    if kwargs.has_key('multi'):
        multi = kwargs.get('multi')
    trans_name = collection.name + '_' + uuid.uuid4().get_hex()

    if is_update:
        type_num = 0
    elif not is_update and is_remove == False:
        type_num = 1
    elif not is_update and is_remove == True:
        type_num = 2
    else:
        raise TransactionException(9999, u'不支持的备份操作')

    col_name = collection.name
    orig_collection = get_orig_collection(collection.name)
    if type_num == 0:
        orig_collection.update(query, {'$push': {'pendingTransactions': str(t_id)}}, multi=multi)
    if type_num == 1:
        orig_collection.update({'_id': {'$in': insert_ids}}, {'$push': {'pendingTransactions': str(t_id)}}, multi=True)

    result = None
    if type_num == 0 or type_num == 2:
        _cur = collection.find(query)
        if not multi:
            _cur = _cur.limit(1)
        for _obj in _cur:
            _obj['orig_id'] = str(_obj['_id'])
            _obj['trans_name'] = trans_name
            _obj['trans_type'] = type_num
            del _obj['_id']
            result = col_backup.insert_one(_obj)
    else:
        _obj = dict()
        _obj['orig_ids'] = map(lambda x: str(x), insert_ids)
        _obj['trans_name'] = trans_name
        _obj['trans_type'] = type_num
        result = col_backup.insert_one(_obj)

    record = {
        'collection_name': collection.name,
        'trans_name': trans_name
    }
    result = col_transaction.update_one({'_id': t_id}, {'$push': {'records': record}})
    pass


def restore_data(record_obj):
    collection_name = record_obj['collection_name']
    trans_name = record_obj['trans_name']
    collection_obj = get_orig_collection(collection_name)

    _cur = col_backup.find({'trans_name': trans_name}).sort([('_id', -1)])
    for _obj in _cur:
        record_id = _obj['_id']
        type_num = _obj['trans_type']
        if type_num == 2 or type_num == 0:
            orig_id = ObjectId(_obj['orig_id'])
            _obj['_id'] = orig_id
            del _obj['orig_id']
            del _obj['trans_name']
            del _obj['trans_type']
            if type_num == 0:
                result = collection_obj.update_one({'_id': orig_id}, {'$set': _obj})
            else:
                result = collection_obj.insert_one(_obj)
        else:
            orig_ids = map(lambda x: ObjectId(x), _obj['orig_ids'])
            result = collection_obj.remove({'_id': {'$in': orig_ids}})

        if result:
            col_backup.delete_one({'_id': record_id})


def rollback(t_id):
    # global g_transaction_obj
    # t_id = g_transaction_obj.id
    transaction_obj = col_transaction.find_one_and_update({'_id': t_id},
                                                          {'$set': {'state': 'canceling',
                                                                    'lastModified': datetime.now()}},
                                                          return_document=ReturnDocument.AFTER)
    for record_obj in transaction_obj['records']:
        restore_data(record_obj)

    col_transaction.update_one({'_id': t_id},
                               {'$set': {'state': 'canceled', 'lastModified': datetime.now()}})
    rollback_close_transaction(t_id)


def clear_trans_data(t_id):
    transaction_obj = col_transaction.find_one({'_id': t_id})
    record_list = transaction_obj['records']
    for record_obj in record_list:
        collection_name = record_obj['collection_name']
        collection_obj = get_orig_collection(collection_name)
        result = collection_obj.update_many({'pendingTransactions': str(t_id)},
                                            {'$pull': {'pendingTransactions': str(t_id)}})


def get_orig_collection(collection_name):
    Database.__getitem__ = orig_get_item
    collection_obj = conn_db[collection_name]
    Database.__getitem__ = new_get_item
    return collection_obj


def get_trans_lock_name():
    return trans_lock_name


def Transaction(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        init_transaction()
        with Lock(redis_lock, get_trans_lock_name(), timeout=5) as look:
            try:
                begin_transaction()
                result = func(*args, **kwargs)
                end_transaction()
                close_transaction(get_transaction_id())
                return result
            except Exception as e:
                rollback(get_transaction_id())
                raise e
            finally:
                release_transaction()

    return wrapper
