
// api请求域名
// window.apiDomain = 'http://api.app.tuoluocaijing.cn';
window.apiDomain = 'https://tapi.xcx.xiaokui.io';
// 用户信息存储key
window.userInfoKey = 'userInfo';
// 网络监听key
window.networkListenerKey = 'network';

/**
 * 打开新窗口
 */
function openWin(name, _url, param){
    var p_url = _url || 'widget://html/' + name + '.html',
        p_param = param || {};
    var win_param = {
        name: name,
        url: p_url,
        pageParam: param
    };
    api.openWin(win_param);
}

/**
 * 打开任务窗口
 */
function openTaskWin(){
    api.openWin({
        name: 'taskWin',
        url: 'widget://html/task.html',
        reload: true
    });
}

/**
 * 打开快讯详情页面
 * @param _id: 快讯id
 */
function openNewsContent(_id){
    if(!_id){
        return;
    }
    // 消息被打开，清除极光推送发送到状态栏的通知，-1表示清除所有
    var ajpush = api.require('ajpush');
    ajpush.clearNotification({ id: -1 },function(ret) {

    });
    api.openWin({
        name: 'newsdetail',
        url: 'widget://html/newsdetail.html',
        pageParam: {
            id: _id,
            load: 1
        }
    });
}

/**
 * 网络请求
 * @param reqType: 请求类型，如 get、post、put、delete
 * @param reqUrl: 请求地址，相对路径
 * @param body: post请求数据，json格式
 * @param fnSuc: 回调函数
 */
function ajax(reqType, reqUrl, data, fnSuc){

    var parms = {
        url: window.apiDomain + reqUrl,
        dataType: 'json',
        method: reqType,
        headers:{
            'Content-Type': 'application/json'
        }
    };
    if(reqType == 'post'){
        api.showProgress({
            title: ''
        });
        parms.data = {
            body: data
        };
    }
    api.ajax(parms, function(ret, err){
        api.hideProgress();
        if (ret) {
            fnSuc && fnSuc(ret);
        }else {
            api.toast({
                msg: '无法连接服务器，请检查您的网络！',
                duration: 2000,
                location: 'middle'
            });
        }
    });
}

/**
 * 获取图片验证码
 * @param ele: 父元素dom选择器
 */
function getImgCode(ele) {
    ajax('get', '/api/user/get_code_key', '', function(ret){
        if(ret.code == 200){
            var _dom = $api.byId(ele),
                code_key = ret.data.code_key,
                _src = window.apiDomain + '/api/user/vercode?code_key=' + code_key + '&t=' + Date.parse(new Date());

            if(_dom.children.length <= 0){
                $api.append(_dom, '<img src="' + _src + '" tapmode onclick="getImgCode(\'img_code_box\');" codeKey="' + code_key + '" />');
            }else{
                $api.attr(_dom.children[0], 'src', _src);
                $api.attr(_dom.children[0], 'codeKey', code_key);
            }
        }else {
            api.toast({
                msg: ret.msg,
                duration: 2000,
                location: 'middle'
            });
        }
    });
}

var timer = null;//短信获取计时器
var plan_second, second = plan_second = 60;//重新发送验证码时间
/**
 * 计时器
 * @param ele_dom: 操作元素dom对象
 */
function countDown(ele_dom) {
    second--;
    if (second > -1) {
        $api.text(ele_dom, second + '秒后重新获取');
        timer = setTimeout(function () {
            countDown(ele_dom);
        }, 1000);//调用自身实现
    } else {
        restTimer(ele_dom);
    }
}

/**
 * 重置计时器
 * @param ele_dom: 操作元素dom对象
 */
function restTimer(ele_dom){
    clearTimeout(timer);
    second = plan_second;
    $api.text(ele_dom, '获取验证码');
    $api.removeCls(ele_dom, 'disabled');
}

/**
 * 验证码获取类
 * @param reqType: 请求类型，reg 注册/ login 登陆
 * @param time: 倒计时间，单位秒
 */
function phoneCode(reqType, time){

    if(typeof(time) === 'number' && time > 0){
        second = plan_second = time;
    }

    var _obj = new Object();
    // 获取验证码
    _obj.getCode = function () {
        var ele_id = 'get_phone_code', ele_dom = $api.byId(ele_id);
        if($api.hasCls(ele_dom, 'disabled') || $api.text(ele_dom).indexOf('秒') > -1){
            return;
        }

        var phone_dom = $api.byId('f_phone'),
            img_code_dom = $api.byId('f_img_code'),

            phone = $api.val(phone_dom),
            img_code = $api.val(img_code_dom),
            img_code_key = $api.attr($api.byId('img_code_box').children[0], 'codeKey');

        var reg_exp = /^1[3|4|5|7|8][0-9]{9}$/;
        if (!reg_exp.test(phone)) {
            api.toast({
                msg: '请填写正确的手机号码',
                duration: 2000,
                location: 'middle'
            });
            return;
        }
        if($api.trim(img_code) == ''){
            api.toast({
                msg: '请输入图片验证码',
                duration: 2000,
                location: 'middle'
            });
            return;
        }
        if(!img_code_key){
            api.toast({
                msg: '图片验证码未能正确获取，请刷新页面重新操作！',
                duration: 2000,
                location: 'middle'
            });
            return;
        }
        $api.addCls(ele_dom, 'disabled');

        var post_data = {
            phone: phone,
            code_key: img_code_key,
            ver_code: img_code,
            req_type: reqType
        };

        ajax('post', '/api/user/send_code', post_data, function(ret){
            $api.removeCls($api.byId('get_phone_code'), 'disabled');
            if(ret.code == 200){
                var ele_dom = $api.byId('get_phone_code');
                $api.text(ele_dom, second + '秒后重新获取');
                setTimeout(function () { countDown(ele_dom) }, 1000);

                api.toast({
                    msg: '手机验证码已发送',
                    duration: 2000,
                    location: 'middle'
                });
                $api.attr($api.byId('f_phone_code'), 'sms_key', ret.sms_key);
            }else {

                api.toast({
                    msg: ret.msg,
                    duration: 2000,
                    location: 'middle'
                });
            }
        });
    }
    return _obj;
}

/**
 * 检查用户登录token是否过期
 * @param valid_callback: 登录有效回调函数
 * @param past_callback: 登录过期或检查失败回调函数
 */
function checkToken(valid_callback, past_callback){
    var userInfo = $api.getStorage(window.userInfoKey);
    if(userInfo && userInfo.token){
        ajax('get', '/api/user/get_info?token=' + userInfo.token, '', function(ret){
            var req_code = ret.code;
            if(req_code == 200){
                valid_callback && valid_callback();
            }else {
                past_callback && past_callback();
            }
            // else if(ret.code == 279){
            //     past_callback && past_callback();
            // }
        });
    }
}

/**
 * 通知服务端 token 失效
 */
function invalidNotification(){
    var userInfo = $api.getStorage(window.userInfoKey);
    if(userInfo && userInfo.token){
        ajax('post', '/api/user/invalid_notification', {
            token: userInfo.token
        }, function(ret){

        });
    }
}

/**
 * 检查用户登录token是否过期
 * @param isTips: 是否进行登录提示
 */
function removeUserInfoStorage(isTips){
    // 登录失效
    $api.rmStorage('userInfo');
    // 对每个页面发送退出通知的事件
    api.sendEvent({
        name: 'logout'
    });
    if(isTips){
        loginTips();
    }
    invalidNotification();
}

/**
 * 登录提示
 */
function loginTips(){
    api.alert({
        title: '请重新登录',
        msg: '您登录凭证已过期，请重新登录！',
    }, function(ret, err) {
        openLogin()
    });
}

/**
 * 打开登录窗口
 */
function openLogin(){
    api.openFrame({
        name: 'login',
        url: 'widget://html/login.html',
        rect: {
            x: 0,
            y: 0,
            w: 'auto',
            h: 'auto'
        },
        bounces: false,
        vScrollBarEnabled: true,
        hScrollBarEnabled: true
    });
}

/**
 * 时间格式化
 */
Date.prototype.format = function(format) {
    var date = {
        "M+": this.getMonth() + 1,
        "d+": this.getDate(),
        "h+": this.getHours(),
        "m+": this.getMinutes(),
        "s+": this.getSeconds(),
        "q+": Math.floor((this.getMonth() + 3) / 3),
        "S+": this.getMilliseconds()
    };
    if (/(y+)/i.test(format)) {
        format = format.replace(RegExp.$1, (this.getFullYear() + '').substr(4 - RegExp.$1.length));
    }
    for (var k in date) {
        if (new RegExp("(" + k + ")").test(format)) {
            format = format.replace(RegExp.$1, RegExp.$1.length == 1 ?
                date[k] : ("00" + date[k]).substr(("" + date[k]).length));
        }
    }
    return format;
};

/**
 * 时间戳转换成几天前
 */
function timeConver(timestamp){
    var nowTime = Date.parse(new Date());
    var time1 = nowTime / 1000 - timestamp;
    time1 = parseInt(time1 / 60);
    if (time1 < 1) {
      return "刚刚";
    } else if (time1 >= 1 && time1 < 60) {
      return time1 + "分钟前";
    } else if (time1 >= 60 && time1 < 1440) {
      var time2 = parseInt(time1 / 60);
      return time2 + "小时前";
    } else if (time1 >= 1440 && time1 < 43200) {
      var time2 = parseInt(time1 / 60 / 24);
      return time2 + "天前";
    } else if (time1 >= 43200 && time1 < 525600) {
      var time2 = parseInt(time1 / 60 / 24 / 30);
      return time2 + "月前";
    } else if (time1 >= 525600) {
      var time2 = parseInt(time1 / 60 / 24 / 30 / 12);
      return time2 + "年前";
    }
}

/**
 * 获取星期几
 * @param _date: 时间对象，如果不传获取当前时间对象
 */
function getWeek(_date){
    var myDate = null;
    if(_date && typeof(_date) == 'object'){
        myDate = _date;
    }else {
        myDate = new Date();
    }
    return '星期' + '日一二三四五六'.charAt(myDate.getDay());
}

/**
 * 数字转千分位
 * @param num: 要转换的数字
 */
function toThousands(num) {
    var num = (num || 0).toString(), result = '';
    while (num.length > 3) {
        result = ',' + num.slice(-3) + result;
        num = num.slice(0, num.length - 3);
    }
    if (num) { result = num + result; }
    return result;
}

/**
 * 初始化容器高度
 */
function initContainerHight(){
	var body_height = document.body.offsetHeight;
	var container = null;
	try{
		container = document.getElementsByClassName('container')[0];
	}catch(e){

	}
	if(!!(container && container.nodeType == 1)){
		var container_height = container.offsetHeight;
		// 容器高度低于body高度则设置容器高度与body高度一致
		if(body_height > container_height){
			// 设置容器高度
			container.style.height = body_height + 'px';
		}
	}

}
