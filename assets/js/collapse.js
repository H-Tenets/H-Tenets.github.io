$(".header").click(function () {

    $header = $(this);
    //获取下一个元素
    $content = $header.next();
    //打开所需的内容 - 切换滑动 - 如果可见，向上滑动，如果不可见则向下滑动。
    $content.slideToggle(500, function () {
        //在slideToggle完成后执行此操作
        //根据内容div的可见性更改标题文本
        $header.text(function () {
            //根据条件更改文本
            return $content.is(":visible") ? "Collapse" : "Expand";
        });
    });

});
