/* A small, untimed exploration of the newsletter's 1729 example. */
(function () {
  'use strict';
  var lab = document.querySelector('[data-math-lab]');
  if (!lab) return;
  var form = lab.querySelector('form'), inputs = Array.from(form.querySelectorAll('input'));
  var feedback = lab.querySelector('[data-lab-feedback]'), total = lab.querySelector('[data-lab-total]');
  var found = lab.querySelector('[data-lab-found]'), hint = lab.querySelector('[data-lab-hint]');
  var svg = lab.querySelector('svg'), pairs = [], hints = 0;
  var ns = 'http://www.w3.org/2000/svg';
  function values() { return inputs.map(function (input) { return input.value === '' ? NaN : Number(input.value); }); }
  function valid(v) { return v.every(function (n) { return Number.isInteger(n) && n >= 1 && n <= 12; }); }
  function path(d, face) {
    var el = document.createElementNS(ns, 'path'); el.setAttribute('d', d); el.setAttribute('class', 'math-lab__' + face); svg.appendChild(el);
  }
  function cube(n, x) {
    var side = n * 10, dx = side * .35, y = 170 - side;
    path('M'+x+' '+y+'h'+side+'v'+side+'h-'+side+'Z', 'front');
    path('M'+x+' '+y+'l'+dx+' -'+dx+'h'+side+'l-'+dx+' '+dx+'Z', 'top');
    path('M'+(x+side)+' '+y+'l'+dx+' -'+dx+'v'+side+'l-'+dx+' '+dx+'Z', 'side');
    for(var i=1;i<n;i++) {
      path('M'+(x+i*10)+' '+y+'v'+side+'M'+x+' '+(y+i*10)+'h'+side,'grid');
    }
  }
  function draw() {
    var v = values(); svg.replaceChildren();
    if (!valid(v)) { total.textContent = 'Choose two whole numbers from 1 to 12.'; return; }
    cube(v[0],35); cube(v[1],245);
    total.textContent = v[0]+'³ + '+v[1]+'³ = '+(v[0]**3+v[1]**3).toLocaleString('en');
  }
  form.addEventListener('input', function () { lab.classList.remove('is-solved'); draw(); });
  form.addEventListener('submit', function (event) {
    event.preventDefault();
    var v = values();
    if (!valid(v)) { feedback.textContent = 'Use whole numbers from 1 to 12 for both cube edges.'; return; }
    var sum = v[0]**3 + v[1]**3, key = v.slice().sort(function(a,b){return a-b;}).join(',');
    if (sum !== 1729) { feedback.textContent = sum.toLocaleString('en')+' is '+Math.abs(1729-sum).toLocaleString('en')+' '+(sum<1729?'below':'above')+' 1729. Try changing one edge.'; return; }
    if (pairs.indexOf(key) !== -1) { feedback.textContent = 'You found that pair already. Reversing the order is the same pair; try two different edges.'; return; }
    pairs.push(key); hints = 0;
    found.textContent = pairs.map(function (pair) { return pair.split(',').join('³ + ')+'³ = 1729'; }).join(' · ');
    if (pairs.length === 2) {
      lab.classList.add('is-solved');
      feedback.textContent = 'Solved! Both different pairs make 1729. Two ways to build the same volume.';
      hint.disabled = true;
    } else feedback.textContent = 'One pair found! Find a different pair to complete the puzzle.';
    lab.querySelector('[data-lab-progress]').textContent = pairs.length+' of 2 pairs found';
  });
  hint.addEventListener('click', function () {
    var target = pairs.indexOf('1,12') === -1 ? [1,12] : [9,10];
    var messages = ['Try an edge of '+target[0]+'. What volume remains after its cube?', 'The remaining volume is '+(1729-target[0]**3)+'. Which whole number cubed gives that?', 'Try edges '+target[0]+' and '+target[1]+', then check the pair.'];
    feedback.textContent = messages[Math.min(hints++, messages.length-1)];
  });
  lab.querySelector('[data-lab-reset]').addEventListener('click', function () {
    pairs = []; hints = 0; form.reset(); hint.disabled = false; found.textContent = 'Your discoveries will appear here.';
    lab.classList.remove('is-solved'); lab.querySelector('[data-lab-progress]').textContent = '0 of 2 pairs found';
    feedback.textContent = 'A fresh start. Find two different pairs of positive cubes that each add up to 1729.';
    draw(); inputs[0].focus({preventScroll:true});
  });
  lab.querySelector('[data-lab-controls]').hidden = false;
  draw();
}());
