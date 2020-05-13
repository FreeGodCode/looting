var navs = [{
	"title": "首页",
	"icon": "fa-globe",
	"href": "index.html",
	"spread":true
}, {
	"title": "资源管理",
	"icon": "fa-tachometer",
	"spread": false,
	"children": [{
		"title": "系统设置",
		"icon": "&#xe614;",
		"href": "resources/config.html"
	}, {
		"title": "模板管理",
		"icon": "&#xe630;",
		"href": "resources/template.html"
	}, {
		"title": "域名管理",
		"icon": "fa-sitemap",
		"href": "resources/domain.html"
	}, {
		"title": "套餐管理",
		"icon": "fa-qrcode",
		"href": "resources/package.html"
	}, {
		"title": "蜘蛛管理",
		"icon": "fa-bug",
		"href": "resources/spider.html"
	}]
}, {
	"title": "账号",
	"icon": "fa-user",
	"spread": false,
	"children": [{
		"title": "账号信息",
		"icon": "fa-list-alt",
		"href": "user/user_inform.html"
	}, {
		"title": "修改密码",
		"icon": " fa-edit",
		"href": "user/revise_psw.html"
	}, {
		"title": "通知公告",
		"icon": "fa-file-sound-o",
		"href": "user/notice.html"
	}, {
		"title": "登录日志",
		"icon": "fa-file-text-o",
		"href": "user/login_log.html"
	}]
}, {
	"title": "文档",
	"icon": "fa-folder-open-o",
	"spread": false,
	"children": [{
		"title": "接口数据",
		"icon": "fa-database",
		"href": "file/interface_data.html"
	},{
		"title": "接口调试工具",
		"icon": "fa-wrench",
		"href": "file/interface_tool.html"
	},{
		"title": "返回码解释",
		"icon": "fa-reply-all",
		"href": "file/back_code.html"
	},{
		"title": "接口参数",
		"icon": "fa-life-ring",
		"href": "file/interface_parameter.html"
	}]
}];