const hamburger = document.getElementById('hamburger');
const overlay = document.getElementById('nav-overlay');
const drawer = document.getElementById('nav-drawer');
const drawerCloseButton = document.getElementById('nav-drawer-close-button');

function openNavigationDrawer() {
  // 要素を可視化する
  overlay.classList.remove('invisible');
  drawer.classList.remove('invisible');

  // アニメーションで要素を表示する
  overlay.classList.remove('opacity-0');
  drawer.classList.remove('-translate-x-full');
}

function closeNavigationDrawer() {
  // アニメーションで要素を非表示にする
  drawer.classList.add('-translate-x-full');
  overlay.classList.add('opacity-0');

  // アニメーションが終わったら要素を非表示にする
  drawer.addEventListener('transitionend', function handleCloseTransition(event) {
    drawer.classList.add('invisible');
    overlay.classList.add('invisible');
  }, { once: true });
}

hamburger.addEventListener('click', openNavigationDrawer);
overlay.addEventListener('click', closeNavigationDrawer);
drawerCloseButton.addEventListener('click', closeNavigationDrawer);
