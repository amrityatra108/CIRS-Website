(function () {
  "use strict";

  var body = document.body;
  if (!body.classList.contains("results")) return;

  var story = document.querySelector(".rj-story");
  var stage = document.querySelector(".rj-stage");
  var canAnimate = story && stage && window.gsap && window.ScrollTrigger;

  document.addEventListener("keydown", function (event) {
    if (event.key === "Tab") body.classList.add("results-keyboard-nav");
  });
  document.addEventListener("pointerdown", function () {
    body.classList.remove("results-keyboard-nav");
  });

  function initDirectory() {
    var form = document.querySelector(".rj-filters");
    var input = document.getElementById("destinationSearch");
    var list = document.getElementById("destinationList");
    var count = document.getElementById("destinationCount");
    var empty = document.getElementById("destinationEmpty");
    if (!form || !input || !list || !count || !empty) return;

    var items = Array.prototype.slice.call(list.querySelectorAll("li"));
    var buttons = Array.prototype.slice.call(form.querySelectorAll("[data-filter]"));
    var region = "all";

    function update() {
      var query = input.value.trim().toLocaleLowerCase();
      var visible = 0;
      items.forEach(function (item) {
        var regionMatch = region === "all" || item.dataset.region === region;
        var textMatch = !query || item.textContent.toLocaleLowerCase().indexOf(query) !== -1;
        item.hidden = !(regionMatch && textMatch);
        if (!item.hidden) visible += 1;
      });
      count.textContent = visible + (visible === 1 ? " verified destination" : " verified destinations");
      empty.hidden = visible !== 0;
    }

    buttons.forEach(function (button) {
      button.addEventListener("click", function () {
        region = button.dataset.filter;
        buttons.forEach(function (candidate) {
          var active = candidate === button;
          candidate.classList.toggle("is-active", active);
          candidate.setAttribute("aria-pressed", String(active));
        });
        update();
      });
    });
    input.addEventListener("input", update);
    form.addEventListener("submit", function (event) {
      event.preventDefault();
      update();
    });
    form.addEventListener("reset", function () {
      window.setTimeout(function () {
        region = "all";
        buttons.forEach(function (button) {
          var active = button.dataset.filter === "all";
          button.classList.toggle("is-active", active);
          button.setAttribute("aria-pressed", String(active));
        });
        update();
      }, 0);
    });
  }

  function initJourney() {
    if (!canAnimate) return;
    var gsap = window.gsap;
    var ScrollTrigger = window.ScrollTrigger;
    gsap.registerPlugin(ScrollTrigger);

    function reveal(targets, trigger, start, stagger) {
      var elements = gsap.utils.toArray(targets);
      if (!elements.length) return;
      gsap.fromTo(elements, { autoAlpha: 0, y: 24 }, {
        autoAlpha: 1,
        y: 0,
        duration: .72,
        stagger: stagger || .08,
        ease: "power3.out",
        scrollTrigger: {
          trigger: trigger || elements[0],
          start: start || "top 84%",
          toggleActions: "play none none reverse"
        }
      });
    }

    function initLowerPageMotion() {
      reveal(".rj-destinations__intro>.rj-label,.rj-destinations__intro>h2,.rj-destinations__intro>p:last-child", ".rj-destinations__intro", "top 78%", .12);

      gsap.utils.toArray(".rj-destination").forEach(function (item) {
        reveal(item.querySelectorAll(":scope>span,:scope>h3,:scope>p"), item, "top 84%", .09);
      });

      reveal(".rj-directory__head .rj-label,.rj-directory__head h2,.rj-directory__head>p", ".rj-directory__head", "top 84%", .1);
      reveal(".rj-filters>label,.rj-searchrow,.rj-filters fieldset,.rj-directory__count", ".rj-filters", "top 88%", .08);

      var directoryRows = gsap.utils.toArray(".rj-directory__list li");
      gsap.set(directoryRows, { autoAlpha: 0, y: 18 });
      ScrollTrigger.batch(directoryRows, {
        start: "top 92%",
        once: true,
        interval: .08,
        batchMax: 4,
        onEnter: function (batch) {
          gsap.to(batch, { autoAlpha: 1, y: 0, duration: .52, stagger: .055, ease: "power2.out", overwrite: "auto" });
        }
      });

      reveal(".rj-final h2,.rj-final nav a", ".rj-final__grid", "top 84%", .09);
    }

    var mm = gsap.matchMedia();
    mm.add("(min-width: 821px) and (prefers-reduced-motion: no-preference)", function () {
      body.classList.add("results-enhanced");

      var words = gsap.utils.toArray(".rj-world__words b");
      var book = story.querySelector(".rj-book");
      var cover = story.querySelector(".rj-cover");

      gsap.set(".rj-book", { xPercent: -25, yPercent: 0, scale: 1, autoAlpha: 0 });
      gsap.set(".rj-cover,.rj-turn", { rotationY: 0 });
      gsap.set(".rj-spread--cbse,.rj-spread--ib,.rj-turn", { autoAlpha: 0 });
      gsap.set(".rj-spread--cbse,.rj-spread--ib", { clipPath: "inset(0 0 0 50%)" });
      gsap.set(".rj-book__pages,.rj-book__shadow", { clipPath: "inset(0 0 0 50%)" });
<<<<<<< HEAD
      gsap.set(".rj-next", { autoAlpha: 0, visibility: "hidden" });
      gsap.set(".rj-next__line", { scaleX: 0 });
=======
>>>>>>> 9da946b2e348966a1b475b04d55b22ea615c2168
      gsap.fromTo(words, { autoAlpha: 0, yPercent: 26 }, {
        autoAlpha: 1, yPercent: 0, duration: .8, stagger: .09, ease: "power3.out", delay: .12
      });
      gsap.fromTo(".rj-world__label,.rj-world__note", { autoAlpha: 0 }, {
        autoAlpha: 1, duration: .7, stagger: .08, ease: "power1.out", delay: .35
      });

      var timeline = gsap.timeline({
        defaults: { ease: "none" },
        scrollTrigger: {
          id: "results-book-journey",
          trigger: story,
          start: "top top",
          end: function () { return "+=" + Math.round(window.innerHeight * 6.5); },
          pin: true,
          scrub: .3,
          invalidateOnRefresh: true,
          anticipatePin: 1
        }
      });

      timeline
        .addLabel("hero", 0)
        .to(".rj-world--cbse img", { xPercent: -2.5, scale: 1.025, duration: 1.1 }, "hero")
        .to(".rj-world--ib img", { xPercent: 2.5, scale: 1.025, duration: 1.1 }, "hero")
        .addLabel("bind", 1.05)
        .to(".rj-world__caption,.rj-scroll", { autoAlpha: 0, duration: .34 }, "bind")
        .to(".rj-split", {
          scaleX: function () { return cover.offsetWidth / stage.clientWidth; },
          scaleY: function () { return cover.offsetHeight / stage.clientHeight; },
          duration: 1.08,
          ease: "power3.inOut"
        }, "bind")
        .to(".rj-book", { autoAlpha: 1, duration: .38 }, "bind+=.7")
        .to(".rj-split", { autoAlpha: 0, duration: .38 }, "bind+=.7")
        .addLabel("cover", 2.13)
        .to({}, { duration: .42 })
        .set(".rj-spread--cbse", { autoAlpha: 1 })
        .addLabel("opening")
        .to(".rj-cover", { rotationY: -90, duration: .55, ease: "power2.in" }, "opening")
        .set(".rj-cover", { autoAlpha: 0 })
        .to(".rj-cover", { rotationY: -178, duration: .55, ease: "power2.out" })
        .to(".rj-book", { xPercent: 0, duration: 1.1, ease: "power2.inOut" }, "opening")
        .to(".rj-book__pages,.rj-book__shadow", { clipPath: "inset(0 0 0 0%)", duration: 1.1, ease: "power2.inOut" }, "opening")
        .to(".rj-spread--cbse", { clipPath: "inset(0 0 0 0%)", duration: 1.1, ease: "power2.inOut" }, "opening")
        .addLabel("cbse")
        .to({}, { duration: .9 })
        .set(".rj-turn", { autoAlpha: 1 })
        .to(".rj-turn", { rotationY: -178, duration: 1.05, ease: "power2.inOut" })
        .set(".rj-spread--cbse", { autoAlpha: 0 }, "<.53")
        .set(".rj-spread--ib", { autoAlpha: 1, clipPath: "inset(0 0 0 0%)" }, "<")
        .addLabel("ib")
        .to({}, { duration: .9 })
        .set(".rj-turn", { autoAlpha: 0 })
        .addLabel("closing")
        .to(".rj-cover", { rotationY: -90, duration: .525, ease: "power2.in" }, "closing")
        .set(".rj-cover", { autoAlpha: 1 })
        .to(".rj-cover", { rotationY: 0, duration: .525, ease: "power2.out" })
        .to(".rj-book", { xPercent: -25, duration: 1.05, ease: "power2.inOut" }, "closing")
        .to(".rj-book__pages,.rj-book__shadow", { clipPath: "inset(0 0 0 50%)", duration: 1.05, ease: "power2.inOut" }, "closing")
        .to(".rj-spread--ib", { clipPath: "inset(0 0 0 50%)", duration: 1.05, ease: "power2.inOut" }, "closing")
        .to(".rj-spread--ib", { autoAlpha: 0, duration: .16 }, "<.72")
        .addLabel("close")
<<<<<<< HEAD
        .to(".rj-book", { scale: .2, yPercent: -18, autoAlpha: 0, duration: .75, ease: "power3.in" })
        .set(".rj-next", { visibility: "visible" })
        .to(".rj-next", { autoAlpha: 1, duration: .45 })
        .to(".rj-next__line", { scaleX: 1, duration: .6 }, "<.08")
        .fromTo(".rj-next p,.rj-next h2,.rj-next>span:last-child", { autoAlpha: 0, y: 22 }, {
          autoAlpha: 1, y: 0, duration: .58, stagger: .1, ease: "power2.out"
        }, "<.18")
        .to({}, { duration: .55 });
=======
        // The book ends closed, on its cover, and the pin releases onto the
        // destinations — which open on "The next chapter" themselves. A
        // full-screen card saying the same thing used to sit between the two.
        .to({}, { duration: .5 });
>>>>>>> 9da946b2e348966a1b475b04d55b22ea615c2168

      var routeNodes = gsap.utils.toArray(".rj-route__node");
      gsap.set(routeNodes, { autoAlpha: 0, scale: 0 });

      var route = gsap.timeline({
        scrollTrigger: {
          id: "results-destination-route",
          trigger: ".rj-destinations",
          start: "top 72%",
          end: "bottom 70%",
          scrub: true
        }
      })
        .to(".rj-route__draw", { strokeDashoffset: 0, duration: 1, ease: "none" }, 0);

      [0.04, 0.36, 0.76, 0.96].forEach(function (position, index) {
        if (!routeNodes[index]) return;
        route.to(routeNodes[index], {
          autoAlpha: 1,
          scale: 1,
          duration: .06,
          ease: "power2.out"
        }, position);
      });

      gsap.utils.toArray(".rj-destination").forEach(function (item) {
        ScrollTrigger.create({
          trigger: item,
          start: "top 72%",
          end: "bottom 45%",
          onToggle: function (self) { item.classList.toggle("is-active", self.isActive); }
        });
      });

      initLowerPageMotion();

      var refresh = function () { ScrollTrigger.refresh(); };
      if (document.fonts && document.fonts.ready) document.fonts.ready.then(refresh);
      window.addEventListener("load", refresh, { once: true });

      return function () {
        route.kill();
        body.classList.remove("results-enhanced");
      };
    });

    mm.add("(max-width: 820px) and (prefers-reduced-motion: no-preference)", function () {
      initLowerPageMotion();
    });

    window.addEventListener("pagehide", function () { mm.revert(); }, { once: true });
  }

  initDirectory();
  initJourney();
}());
