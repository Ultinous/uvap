window.addEventListener('load', function() {
  function button(label, ariaLabel, icon, className) {
    const btn = document.createElement('button');
    btn.classList.add('btnIcon');
    btn.setAttribute('type', 'button');
    btn.setAttribute('aria-label', ariaLabel);
    btn.innerHTML =
      '<div class="btnIcon__body">' +
      icon +
      '<strong class="btnIcon__label">' +
      label +
      '</strong>' +
      '</div>';
    return btn;
  }

  function addButtons(codeBlockSelector, btn) {
    document.querySelectorAll(codeBlockSelector).forEach(function(code) {
      var myBtn = btn.cloneNode(true);
      code.appendChild(myBtn);
      var codeClone = code.cloneNode(true);
      code.parentNode.querySelectorAll('.static-file-code-block').forEach(function(codeBlock) {
        codeBlock.insertBefore(codeClone, codeBlock.childNodes[0]);
      });
      code.parentNode.removeChild(code);
    });
  }

  const downloadIcon =
    '<svg width="12" height="12" viewBox="0 0 12 12" xmlns="http://www.w3.org/2000/svg"><path fill="currentColor" d="m10.05082,4.28897c0.00873,-0.09486 0.01379,-0.1907 0.01379,-0.28751c0,-1.6793 -1.28601,-3.04045 -2.8726,-3.04045c-1.23131,0 -2.27878,0.82165 -2.68738,1.97459c-0.27071,-0.31426 -0.65679,-0.51517 -1.09021,-0.51517c-0.8172,0 -1.47951,0.70101 -1.47951,1.56595c0,0.10216 0.01057,0.20189 0.0285,0.29821c-1.09021,0.19021 -1.92441,1.18505 -1.92441,2.39247c0,1.34364 1.02908,2.43236 2.29808,2.43236l1.56453,0l-0.32495,-0.34394c-0.17328,-0.1834 -0.26888,-0.42761 -0.26888,-0.68739c0,-0.25929 0.0956,-0.5035 0.26888,-0.6869l0.25555,-0.27097c0.18385,-0.1941 0.43066,-0.3055 0.6761,-0.3055c0.01241,0 0.02482,0 0.03677,0.00097l0,-0.22962c0,-0.53707 0.41274,-0.97392 0.91923,-0.97392l1.50111,0c0.50696,0 0.91923,0.43685 0.91923,0.97392l0,0.22962c0.01241,-0.00097 0.02482,-0.00097 0.03723,-0.00097c0.24498,0 0.49179,0.1114 0.67564,0.30648l0.25601,0.26853c0.3585,0.37994 0.3585,0.99727 0,1.37574l-0.32449,0.34394l1.10446,0c1.26946,0 2.29808,-1.08873 2.29808,-2.43236c0.00046,-1.19234 -0.81122,-2.17988 -1.88075,-2.38809zm-1.52225,3.4452l-0.25555,-0.26999c-0.17925,-0.18924 -0.44307,-0.21891 -0.58647,-0.06665c-0.1434,0.15178 -0.26106,0.0574 -0.26106,-0.21016l0,-0.60225c0,-0.26756 -0.20729,-0.48647 -0.45962,-0.48647l-1.50065,0c-0.25279,0 -0.45962,0.21891 -0.45962,0.48647l0,0.60225c0,0.26756 -0.11766,0.36194 -0.26152,0.21016c-0.1434,-0.15227 -0.40768,-0.12259 -0.58647,0.06665l-0.25555,0.26999c-0.17925,0.18924 -0.17925,0.49815 -0.00046,0.68739l1.98922,2.10691c0.08917,0.09438 0.20729,0.14156 0.32495,0.14156s0.23532,-0.04719 0.32495,-0.14156l1.98876,-2.10691c0.17879,-0.18875 0.17833,-0.49815 -0.00092,-0.68739z" fill-rule="evenodd"/></svg>';

  addButtons(
    '.btnDownload',
    button('Download', 'Download code as raw file', downloadIcon),
  );
});
