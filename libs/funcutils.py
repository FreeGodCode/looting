# -*- coding: utf8 -*-
# author: tefsky

def get_func_default_values(func):
    return func.func_defaults


def get_func_default_val_dict(func):
    names = get_func_arg_names(func)
    names = list(reversed(names))
    default_vals = get_func_default_values(func)
    default_count = len(default_vals)
    if default_count == 0:
        return dict()
    def_names = reversed(names[:default_count])
    val_dict = dict(zip(def_names, default_vals))
    return val_dict


def get_func_params(func, args, kwargs):
    arg_count = get_func_arg_count(func)
    names = get_func_arg_names(func)
    default_vals = get_func_default_values(func)
    default_count = len(default_vals)
    if default_count == 0:
        return dict()
    real_arg_count = len(args)
    count = arg_count - real_arg_count
    p_args = list(default_vals[:count])
    p_args = list(list(args) + p_args)
    for arg in kwargs.keys():
        idx = names.index(arg)
        p_args[idx] = kwargs[arg]
    return p_args


def get_func_params_dict(func, args, kwargs):
    names = get_func_arg_names(func)
    params = get_func_params(func, args, kwargs)
    return dict(zip(names, params))


def get_func_arg_count(func_obj):
    return func_obj.func_code.co_argcount


def get_func_arg_names(func_obj):
    count = get_func_arg_count(func_obj)
    if count == 0:
        return list()
    return func_obj.func_code.co_varnames[0:count]


def get_func_path(func_obj):
    return func_obj.func_globals['__file__']


def get_func_package(func_obj):
    return func_obj.func_globals['__package__']


def get_func_name(func_obj):
    return func_obj.func_name


def get_func_full_name(func_obj):
    return func_obj.func_globals['__name__'] + '.' + get_func_name(func_obj)