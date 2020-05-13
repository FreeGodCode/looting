layui.define(['setter', 'admin'], function(exports){
  var setter = layui.setter
  ,element = layui.element
  ,admin = layui.admin
  ,tabsPage = admin.tabsPage
  ,view = layui.view

  //打开标签页
  ,addTabsPage = function(url, text){
    //遍历页签选项卡
    var matchTo
    ,tabs = $('#LAY_app_tabsheader>li')
    ,path = url.replace(/(^http(s*):)|(\?[\s\S]*$)/g, '');

    text = text || '新标签页';
    tabs.each(function(index){
      var li = $(this)
      ,layid = li.attr('lay-id');
      if(layid === url){
        matchTo = true;
        tabsPage.index = index;
      }
    });
    if(setter.pageTabs){
      //如果未在选项卡中匹配到，则追加选项卡
      if(!matchTo){
        $(APP_BODY).append([
          '<div class="layadmin-tabsbody-item layui-show">'
            ,'<iframe src="'+ url +'" frameborder="0" class="layadmin-iframe"></iframe>'
          ,'</div>'
        ].join(''));
        tabsPage.index = tabs.length;
        element.tabAdd(FILTER_TAB_TBAS, {
          title: '<span>'+ text +'</span>'
          ,id: url
          ,attr: path
        });
      }
    } else {
      var iframe = admin.tabsBody(admin.tabsPage.index).find('.layadmin-iframe');
      iframe[0].contentWindow.location.href = url;
    }

    //定位当前tabs
    element.tabChange(FILTER_TAB_TBAS, url);
    admin.tabsBodyChange(tabsPage.index, {
      url: url
      ,text: text
    });
  }
  ,changeTabsPage = function(url, text){
    admin.closeThisTabs();
    //定位当前tabs
    element.tabChange(FILTER_TAB_TBAS, url);
    admin.tabsBodyChange(tabsPage.index, {
      url: url
      ,text: text
    });

  }
  ,APP_BODY = '#LAY_app_body', FILTER_TAB_TBAS = 'layadmin-layout-tabs'
  ,$ = layui.$, $win = $(window);

  //对外输出
  exports('tabs', {
    addTabsPage: addTabsPage,
    changeTabsPage:changeTabsPage
  });
});
