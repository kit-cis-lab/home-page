const hamburger = document.getElementById('hamburger');
const overlay = document.getElementById('overlay');
const drawer = document.getElementById('drawer');
const drawerCloseButton = document.getElementById('drawerCloseButton');

function openDrawer() {
  overlay.classList.remove('hidden');
  drawer.classList.remove('hidden');
  
  setTimeout(() => {
    drawer.classList.remove('translate-x-full');
    drawer.classList.add('translate-x-0');
  }, 10); // overlay と drawer が表示されるのを待つ
}

function closeDrawer() {
  drawer.classList.remove('translate-x-0');
  drawer.classList.add('translate-x-full');

  setTimeout(() => {
    overlay.classList.add('hidden');
    drawer.classList.add('hidden');
  }, 300); // drawer が完全に閉じるのを待つ
}

hamburger.addEventListener('click', openDrawer);
overlay.addEventListener('click', closeDrawer);
drawerCloseButton.addEventListener('click', closeDrawer);
