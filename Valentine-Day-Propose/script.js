/* =========================================
   BRIDGERTON THEME: INTERACTIVITY ENGINE
   ========================================= */

document.addEventListener('DOMContentLoaded', () => {

    // Element References
    const noBtn = document.getElementById('no-btn');
    const noBtnWrapper = document.getElementById('no-btn-wrapper');
    const bgMusic = document.getElementById('bg-music');
    const blastSound = document.getElementById('blast-sound');
    const yeahSound = document.getElementById('yeah-sound');
    const musicToggle = document.getElementById('music-toggle');
    const wingL = document.getElementById('wing-l');
    const wingR = document.getElementById('wing-r');
    const yesBtn = document.getElementById('yes-btn');
    const buttonsContainer = document.querySelector('.buttons');
    const container = document.getElementById('container');
    const finalScreen = document.getElementById('final-screen');
    const finalImage = document.getElementById('final-image');
    const bgReveal = document.getElementById('bg-reveal');

    // =========================================
    // 1. GRID GENERATION (RESPONSIVE)
    // =========================================
    function generateGrid() {
        const w = window.innerWidth;
        const h = window.innerHeight;

        // Overflow buffer to prevent gaps on resize
        const cols = Math.ceil(w / 150) + 4;
        const rows = Math.ceil(h / 150) + 4;
        const total = cols * rows;

        let html = '';
        for (let i = 0; i < total; i++) {
            html += '<img src="Meme.png" alt="">';
        }
        bgReveal.innerHTML = html;
    }

    generateGrid();
    window.addEventListener('resize', generateGrid);

    // =========================================
    // 2. STATE MANAGEMENT (HOVER/TOUCH)
    // =========================================

    const mainHeading = document.querySelector('h1');
    const originalText = mainHeading.innerHTML;

    const showReveal = () => {
        document.body.classList.add('reveal-active');
        mainHeading.innerHTML = "I knew it, MySaniea doesn’t make mistakes";
    };
    const hideReveal = () => {
        document.body.classList.remove('reveal-active');
        mainHeading.innerHTML = originalText;
    };

    // Mouse
    yesBtn.addEventListener('mouseenter', showReveal);
    yesBtn.addEventListener('mouseleave', hideReveal);

    // Touch
    yesBtn.addEventListener('touchstart', (e) => {
        showReveal();
    }, { passive: true });

    yesBtn.addEventListener('touchend', (e) => {
        hideReveal();
    }, { passive: true });

    // =========================================
    // 3. PHYSICS ENGINE (AVASIVE BUTTON)
    // =========================================

    // Aggressive Event Blocking
    const blockEvent = (e) => {
        e.preventDefault();
        e.stopImmediatePropagation();
        return false;
    };
    ['click', 'mousedown', 'mouseup', 'pointerdown', 'touchstart', 'touchend'].forEach(evt => {
        noBtn.addEventListener(evt, blockEvent, { capture: true });
    });

    const state = {
        active: false,
        x: 0,
        y: 0,
        vx: 0,
        vy: 0,
        ax: 0,
        ay: 0,
        rotation: 0,
    };

    let mouseX = -1000;
    let mouseY = -1000;

    function updateMouse(x, y) {
        mouseX = x;
        mouseY = y;

        if (!state.active) {
            const rect = noBtn.getBoundingClientRect();
            const centerX = rect.left + rect.width / 2;
            const centerY = rect.top + rect.height / 2;
            const dist = Math.hypot(x - centerX, y - centerY);

            // Trigger when actually close (reverting to sensible 300px)
            if (dist < 300) {
                activatePhysics();
            }
        }
    }

    document.addEventListener('mousemove', e => updateMouse(e.clientX, e.clientY));
    document.addEventListener('touchmove', e => {
        if (e.touches.length) updateMouse(e.touches[0].clientX, e.touches[0].clientY);
    }, { passive: false });

    // Ensure direct touches monitor too
    noBtn.addEventListener('touchstart', (e) => {
        e.preventDefault();
        if (!state.active) activatePhysics();
    }, { passive: false });

    // Mouseover trap
    noBtn.addEventListener('mouseover', () => {
        if (!state.active) activatePhysics();
    });

    function activatePhysics() {
        state.active = true;
        const rect = noBtn.getBoundingClientRect();
        state.x = rect.left;
        state.y = rect.top;

        // Fix wrapper dimensions before transition
        noBtnWrapper.style.width = rect.width + 'px';
        noBtnWrapper.style.height = rect.height + 'px';
        void noBtnWrapper.offsetWidth;

        // Promote button to fixed
        noBtn.style.position = 'fixed';
        noBtn.style.left = state.x + 'px';
        noBtn.style.top = state.y + 'px';
        noBtn.style.margin = '0';

        // Disable interactions immediately
        noBtn.style.pointerEvents = 'none';

        // Collapse layout
        noBtnWrapper.style.width = '0px';
        buttonsContainer.style.gap = '0px';

        // Start wing animation
        noBtnWrapper.classList.add('is-flying');

        requestAnimationFrame(animatePhysics);
    }

    // Mouse Velocity Tracking
    let lastTime = performance.now();
    let prevMouseX = mouseX;
    let prevMouseY = mouseY;

    // --- Main Physics Loop for "No" Button ---
    function animatePhysics() {
        if (container.style.opacity === '0') return;

        const now = performance.now();
        const dt = (now - lastTime) / 16.66; // Normalize to ~60fps
        lastTime = now;

        const rect = noBtn.getBoundingClientRect();
        const width = rect.width;
        const height = rect.height;
        const centerX = state.x + width / 2;
        const centerY = state.y + height / 2;

        const dx = centerX - mouseX;
        const dy = centerY - mouseY;
        const dist = Math.hypot(dx, dy);

        // Calculate Mouse Velocity (Pixel per frame approx)
        const mouseVx = mouseX - prevMouseX;
        const mouseVy = mouseY - prevMouseY;
        prevMouseX = mouseX;
        prevMouseY = mouseY;

        // --- CORNER TRAP FAILSAFE ---
        // If the button is stuck in a corner, TELEPORT to center
        const cornerThreshold = 150;
        const viewportW = window.innerWidth;
        const viewportH = window.innerHeight;

        const inLeft = state.x < cornerThreshold;
        const inRight = state.x > viewportW - width - cornerThreshold;
        const inTop = state.y < cornerThreshold;
        const inBottom = state.y > viewportH - height - cornerThreshold;

        // If in ANY corner (e.g. Top-Left) AND user is close
        if ((inLeft || inRight) && (inTop || inBottom)) {
            if (dist < 500) { // If user is even remotely threatening
                state.x = viewportW / 2 - width / 2;
                state.y = viewportH / 2 - height / 2;
                // Reset velocity to 0 to stop wild spinning after teleport
                state.vx = 0;
                state.vy = 0;
            }
        }

        // --- ULTIMATE FAILSAFE: FORCEFIELD TELEPORT ---
        // If they get within 300px (massive radius), TELEPORT INSTANTLY.
        // This prevents the cursor from EVER overlapping.
        if (dist < 300) {
            const jumpDist = 500 + Math.random() * 200; // Random long jump
            state.x += (dx / dist) * jumpDist;
            state.y += (dy / dist) * jumpDist;
        }

        // Constants - Tuned for "Ghost Mode"
        const predictiveRadius = 800; // Detect from almost full screen
        const panicRadius = 400;
        let repulsionForce = 150.0;   // INSTANT ACCELERATION
        const friction = 0.98;
        const maxVelocity = 250;      // TELEPORT SPEED

        // Repulsion Logic
        if (dist < predictiveRadius) {
            let force = (predictiveRadius - dist) / predictiveRadius;

            force = force * force;

            // Simple Massive Repulsion
            if (dist < panicRadius) force *= 5.0;

            state.ax = (dx / dist) * force * repulsionForce;
            state.ay = (dy / dist) * force * repulsionForce;

            // Jitter 
            if (dist < 400 && Math.hypot(state.vx, state.vy) < 10) {
                state.vx += (Math.random() - 0.5) * 100;
                state.vy += (Math.random() - 0.5) * 100;
            }

        } else {
            state.ax = 0;
            state.ay = 0;
        }

        // Center Gravity (Don't get stuck in corners)
        const edgeThreshold = 100;
        // viewportW and viewportH are already defined above, no need to redefine
        // const viewportW = window.innerWidth;
        // const viewportH = window.innerHeight;

        if ((state.x < edgeThreshold || state.x > viewportW - width - edgeThreshold) &&
            (state.y < edgeThreshold || state.y > viewportH - height - edgeThreshold)) {

            const centerDx = (viewportW / 2) - centerX;
            const centerDy = (viewportH / 2) - centerY;
            const centerDist = Math.hypot(centerDx, centerDy);

            if (centerDist > 0) {
                state.ax += (centerDx / centerDist) * 5.0;
                state.ay += (centerDy / centerDist) * 5.0;
            }
        }

        state.vx += state.ax;
        state.vy += state.ay;

        const speed = Math.hypot(state.vx, state.vy);
        if (speed > maxVelocity) {
            state.vx = (state.vx / speed) * maxVelocity;
            state.vy = (state.vy / speed) * maxVelocity;
        }

        state.vx *= friction;
        state.vy *= friction;
        state.x += state.vx;
        state.y += state.vy;

        // Boundaries
        const padding = 20;
        const maxX = viewportW - width - padding;
        const maxY = viewportH - height - padding;

        if (state.x < padding) { state.x = padding; state.vx *= -0.8; }
        if (state.x > maxX) { state.x = maxX; state.vx *= -0.8; }
        if (state.y < padding) { state.y = padding; state.vy *= -0.8; }
        if (state.y > maxY) { state.y = maxY; state.vy *= -0.8; }

        // Rotation
        const targetRotation = state.vx * 1.5;
        state.rotation = state.rotation * 0.9 + targetRotation * 0.1;

        // Wing Video Sync
        const newDuration = Math.max(0.1, 0.5 - (speed * 0.015)) + 's';
        if (wingL) wingL.style.animationDuration = newDuration;
        if (wingR) wingR.style.animationDuration = newDuration;

        noBtn.style.left = state.x + 'px';
        noBtn.style.top = state.y + 'px';
        noBtn.style.transform = `rotate(${state.rotation}deg)`;

        requestAnimationFrame(animatePhysics);
    }

    // =========================================
    // 4. CELEBRATION (FLOWER BURST)
    // =========================================
    yesBtn.addEventListener('click', () => {
        document.body.classList.remove('reveal-active');
        bgReveal.style.transition = 'none';
        bgReveal.style.opacity = '0';

        const rect = yesBtn.getBoundingClientRect();
        const originX = rect.left + rect.width / 2;
        const originY = rect.top + rect.height / 2;

        setTimeout(() => {
            container.style.opacity = '0';
            if (noBtn) noBtn.style.opacity = '0';
            container.style.pointerEvents = 'none';
        }, 100);

        createFlowerBurst(originX, originY);

        // Play sound effects
        blastSound.play().catch(e => console.log("Blast sound blocked:", e));
        setTimeout(() => {
            yeahSound.play().catch(e => console.log("Yeah sound blocked:", e));
        }, 200);

        setTimeout(() => {
            finalScreen.style.opacity = '1';
            finalScreen.style.pointerEvents = 'auto';
            finalImage.style.transform = 'scale(1)';
        }, 1500);
    });

    function createFlowerBurst(x, y) {
        const particleCount = 200; // Balanced for quality and smoothness
        const varieties = ['🌹', '🦋', '💍', '💌', '⚜️', '🥀', '👒', '☕', '🐝', '💠', '💜', '🌸', '✨', '👑', '🦢'];

        for (let i = 0; i < particleCount; i++) {
            const el = document.createElement('div');
            el.classList.add('flower');
            el.innerText = varieties[Math.floor(Math.random() * varieties.length)];

            let startX, startY;
            if (Math.random() > 0.5) {
                startX = x;
                startY = y;
            } else {
                startX = Math.random() * window.innerWidth;
                startY = Math.random() * window.innerHeight - 100;
            }

            el.style.left = startX + 'px';
            el.style.top = startY + 'px';
            el.style.fontSize = (Math.random() * 30 + 10) + 'px';

            if (Math.random() > 0.7) {
                el.style.filter = `blur(${Math.random() * 3}px)`;
                el.style.opacity = 0.7;
            }

            document.body.appendChild(el);

            const angle = Math.random() * Math.PI * 2;
            const velocity = Math.random() * 30 + 10;
            let vx = Math.cos(angle) * velocity;
            let vy = Math.sin(angle) * velocity;
            vy -= Math.random() * 15;

            let posX = startX;
            let posY = startY;
            let velX = vx;
            let velY = vy;
            let gravity = 0.6;
            let drag = 0.95;
            let rotation = Math.random() * 360;
            let rotSpeed = (Math.random() - 0.5) * 20;

            function updateParticle() {
                posX += velX;
                posY += velY;
                velY += gravity;
                velX *= drag;
                velY *= drag;
                rotation += rotSpeed;
                el.style.transform = `translate3d(${posX - startX}px, ${posY - startY}px, 0) rotate(${rotation}deg)`;

                if (posY > window.innerHeight + 100) {
                    el.remove();
                } else {
                    requestAnimationFrame(updateParticle);
                }
            }
            requestAnimationFrame(updateParticle);
        }
    }
});
