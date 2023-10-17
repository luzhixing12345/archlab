// 这里保存


// 美化选择框
// - [ ] xxx
// - [x] aaa
var inputs = document.getElementsByTagName('input')
for(var i=0;i<inputs.length;i++) {
    inputs[i].removeAttribute('disabled')
    inputs[i].onclick = function() {
        return false;
    }
}

var markdown_part = document.querySelector(".markdown-body");


var currentUrl = window.location.href.slice(0, -1);
var dirTree = document.querySelector(".dir-tree");
var links = dirTree.querySelectorAll("a");

// 如果保存的主题存在,则设置当前主题为保存的主题
const savedTheme = localStorage.getItem('theme');
if (savedTheme !== null) {
    if (savedTheme === 'light') {
        markdown_part.className = 'markdown-body markdown-light'
    } else {
        markdown_part.className = 'markdown-body markdown-dark'
    }
}
links.forEach(function(link) {
  if (link.href === currentUrl) {
    link.scrollIntoView({block: 'center', inline:'nearest', container: dirTree });
    if (savedTheme) {
        if (savedTheme == 'dark') {
            link.classList.add("link-active-dark");
        } else {
            link.classList.add("link-active");
        }
    } else {
        link.classList.add("link-active");
    }
  }
});

