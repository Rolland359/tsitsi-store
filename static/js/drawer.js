document.addEventListener('DOMContentLoaded', function() {
    const drawer = document.getElementById('myDrawer');
    const overlay = document.getElementById('drawerOverlay');
    const openBtn = document.getElementById('openDrawerBtn');
    const closeBtn = document.getElementById('closeDrawerBtn');

    function toggleDrawer() {
        drawer.classList.toggle('active');
        overlay.classList.toggle('active');
        // Empêche le défilement de la page quand le menu est ouvert
        if (drawer.classList.contains('active')) {
            document.body.style.overflow = 'hidden';
        } else {
            document.body.style.overflow = '';
        }
    }

    if(openBtn) openBtn.addEventListener('click', toggleDrawer);
    if(closeBtn) closeBtn.addEventListener('click', toggleDrawer);
    if(overlay) overlay.addEventListener('click', toggleDrawer);
});