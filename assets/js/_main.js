/* ==========================================================================
   我们想在模板中使用的各种函数
   ========================================================================== */

// 确定主题切换的预期状态，可以是"dark"、"light"或
// "system"。默认是"system"。
let determineThemeSetting = () => {
  let themeSetting = localStorage.getItem("theme");
  return (themeSetting != "dark" && themeSetting != "light" && themeSetting != "system") ? "system" : themeSetting;
};

// 确定计算的主题，可以是"dark"或"light"。如果主题设置是
// "system"，则根据用户的系统偏好确定计算的主题。
let determineComputedTheme = () => {
  let themeSetting = determineThemeSetting();
  if (themeSetting != "system") {
    return themeSetting;
  }
  return (userPref && userPref("(prefers-color-scheme: dark)").matches) ? "dark" : "light";
};

// 检测操作系统/浏览器偏好
const browserPref = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';

// 在页面加载时或显式调用时设置主题
let setTheme = (theme) => {
  const use_theme =
    theme ||
    localStorage.getItem("theme") ||
    $("html").attr("data-theme") ||
    browserPref;

  if (use_theme === "dark") {
    $("html").attr("data-theme", "dark");
    $("#theme-icon").removeClass("fa-sun").addClass("fa-moon");
  } else if (use_theme === "light") {
    $("html").removeAttr("data-theme");
    $("#theme-icon").removeClass("fa-moon").addClass("fa-sun");
  }
};

// 手动切换主题
var toggleTheme = () => {
  const current_theme = $("html").attr("data-theme");
  const new_theme = current_theme === "dark" ? "light" : "dark";
  localStorage.setItem("theme", new_theme);
  setTheme(new_theme);
};

/* ==========================================================================
   Plotly集成脚本，以便渲染Markdown代码块
   ========================================================================== */

// 从代码块读取Plotly数据，隐藏它，并将图表渲染为新节点。这允许在切换主题时检索JSON数据。
// 只有当页面上实际存在数据时才应添加监听器。
import { plotlyDarkLayout, plotlyLightLayout } from './theme.js';
let plotlyElements = document.querySelectorAll("pre>code.language-plotly");
if (plotlyElements.length > 0) {
  document.addEventListener("readystatechange", () => {
    if (document.readyState === "complete") {
      plotlyElements.forEach((elem) => {
        // 解析Plotly JSON数据并隐藏它
        var jsonData = JSON.parse(elem.textContent);
        elem.parentElement.classList.add("hidden");

        // 添加Plotly节点
        let chartElement = document.createElement("div");
        elem.parentElement.after(chartElement);

        // 设置图表的主题并渲染它
        const theme = (determineComputedTheme() === "dark") ? plotlyDarkLayout : plotlyLightLayout;
        if (jsonData.layout) {
          jsonData.layout.template = (jsonData.layout.template) ? { ...theme, ...jsonData.layout.template } : theme;
        } else {
          jsonData.layout = { template: theme };
        }
        Plotly.react(chartElement, jsonData.data, jsonData.layout);
      });
    }
  });
}

/* ==========================================================================
   页面完全加载时应执行的操作
   ========================================================================== */

$(document).ready(function () {
  // SCSS设置 - 这些应该与相关文件中的设置相同
  const scssLarge = 925;          // 像素，来自/_sass/_themes.scss
  const scssMastheadHeight = 70;  // 像素，来自当前主题（例如，/_sass/theme/_default.scss）

  // 如果用户没有选择主题，则遵循操作系统偏好
  setTheme();
  window.matchMedia('(prefers-color-scheme: dark)')
        .addEventListener("change", (e) => {
          if (!localStorage.getItem("theme")) {
            setTheme(e.matches ? "dark" : "light");
          }
        });

  // 启用主题切换
  $('#theme-toggle').on('click', toggleTheme);

  // 启用粘性页脚
  var bumpIt = function () {
    $("body").css("padding-bottom", "0");
    $("body").css("margin-bottom", $(".page__footer").outerHeight(true));
  }
  $(window).resize(function () {
    didResize = true;
  });
  setInterval(function () {
    if (didResize) {
      didResize = false;
      bumpIt();
    }}, 250);
  var didResize = false;
  bumpIt();

  // FitVids初始化
  fitvids();

  // 跟随菜单下拉
  $(".author__urls-wrapper button").on("click", function () {
    $(".author__urls").fadeToggle("fast", function () { });
    $(".author__urls-wrapper button").toggleClass("open");
  });

  // 如果在窗口调整大小时切换，则恢复跟随菜单
  jQuery(window).on('resize', function () {
    if ($('.author__urls.social-icons').css('display') == 'none' && $(window).width() >= scssLarge) {
      $(".author__urls").css('display', 'block')
    }
  });

  // 初始化平滑滚动，这需要比固定的masthead高度略大
  $("a").smoothScroll({
    offset: -scssMastheadHeight,
    preventDefault: false,
  });

});
