const config = {
    scenes: [
        { type: 'theme', text: 'Rose Day showed intention.\\nPropose Day brought clarity and courage.' },
        { vo: 'assets/audio/choc_sc1.mp3', text: 'Not every day needs courage.\\nSome days need comfort.', type: 'intro' },
        {
            vo: 'assets/audio/choc_sc2.mp3', text: 'After saying what mattered,\\nhe didn\\'t feel the need to prove anything.', boy: true, chocolate: 'in_hand' },
        {
                vo: 'assets/audio/choc_sc3.mp3', text: 'This wasn\\'t about a gesture.\\nIt was about sharing something ordinary.', boy: true, chocolate: 'looking' },
        {
                    vo: 'assets/audio/choc_sc4.mp3', text: 'She noticed the shift.\\nThis wasn\\'t effort.This was ease.', girl: true },
        { vo: 'assets/audio/choc_sc5.mp3', text: 'I thought you might like this.', both: true, chocolate: 'offering' },
        { text: '', both: true, chocolate: 'transferring', silent: true },  // Silent transfer
        { vo: 'assets/audio/choc_sc7.mp3', text: 'Some connections grow louder.\\nOthers grow easier.', both: true, chocolate: 'received' },
        { vo: 'assets/audio/choc_sc8.mp3', text: 'Chocolate Day isn\\'t about sweetness.\\nIt\\'s about choosing comfort after honesty.', both: true, chocolate: 'received' },
        { type: 'final', text: 'Chocolate Day' }
    ],
    bgColor: '#D3D3D3',
    textColor: '#2D2D2D'
};

const svg = document.getElementById('character-svg');
const subtitleBox = document.getElementById('subtitles');
const overlay = document.getElementById('overlay');
const startBtn = document.getElementById('start-btn');

let currentIdx = 0;
let sceneStartTime = 0;
let isPaused = false;
let pauseStartTime = 0;
let currentAudio = null;
let totalPausedTime = 0;

function drawChocolate(x, y, angle = 0) {
    const g = document.createElementNS("http://www.w3.org/2000/svg", "g");

    const rect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
    rect.setAttribute("x", x - 15);
    rect.setAttribute("y", y - 10);
    rect.setAttribute("width", 30);
    rect.setAttribute("height", 20);
    rect.setAttribute("rx", 3);
    rect.setAttribute("fill", "#8B4513");
    rect.setAttribute("stroke", "#653213");
    rect.setAttribute("stroke-width", 2);
    g.appendChild(rect);

    // Wrapper highlights
    const line1 = document.createElementNS("http://www.w3.org/2000/svg", "line");
    line1.setAttribute("x1", x - 10);
    line1.setAttribute("y1", y - 7);
    line1.setAttribute("x2", x + 10);
    line1.setAttribute("y2", y - 7);
    line1.setAttribute("stroke", "#A05A28");
    line1.setAttribute("stroke-width", 1);
    g.appendChild(line1);

    const line2 = document.createElementNS("http://www.w3.org/2000/svg", "line");
    line2.setAttribute("x1", x - 10);
    line2.setAttribute("y1", y + 7);
    line2.setAttribute("x2", x + 10);
    line2.setAttribute("y2", y + 7);
    line2.setAttribute("stroke", "#A05A28");
    line2.setAttribute("stroke-width", 1);
    g.appendChild(line2);

    if (angle !== 0) {
        g.setAttribute("transform", `rotate(${angle}, ${x}, ${y})`);
    }

    return g;
}

function drawHuman(x, y, isWoman = false, expression = 'neutral', breath = 0, hasChocolate = false, step = 0) {
    const scale = isWoman ? 0.78 : 0.95;
    const charX = x + (isWoman ? -step : 0);
    const charY = y - (isWoman ? breath * 0.3 : breath * 0.4);
    const g = document.createElementNS("http://www.w3.org/2000/svg", "g");

    // Clothing colors
    let clothingColor, clothingAccent, shirtColor, pantsColor;
    if (isWoman) {
        clothingColor = "#E6BED8";  // Soft lavender/pink
        clothingAccent = "#D2AAC8";
    } else {
        shirtColor = "#C8D2DC";  // Light blue-grey
        pantsColor = "#3C465A";  // Dark grey
    }

    const shadow = document.createElementNS("http://www.w3.org/2000/svg", "ellipse");
    shadow.setAttribute("cx", charX);
    shadow.setAttribute("cy", y + 5);
    shadow.setAttribute("rx", 55 * scale);
    shadow.setAttribute("ry", 10);
    shadow.setAttribute("fill", "rgba(0,0,0,0.1)");
    g.appendChild(shadow);

    const headR = 30 * scale;
    const sW = (isWoman ? 52 : 68) * scale;
    const torsoH = (110 + breath) * scale;
    const hipW = (isWoman ? 56 : 48) * scale;
    const legH = 120 * scale;
    const baseHipsY = charY - legH;
    const shoulderY = baseHipsY - torsoH;
    const headY = shoulderY - 10 * scale - headR;

    // === CLOTHING LAYER ===

    if (!isWoman) {
        // Boy: Pants (legs with color)
        [-1, 1].forEach(side => {
            const lx = charX + side * (hipW / 4);
            const leg = document.createElementNS("http://www.w3.org/2000/svg", "line");
            leg.setAttribute("x1", lx);
            leg.setAttribute("y1", baseHipsY);
            leg.setAttribute("x2", lx);
            leg.setAttribute("y2", charY);
            leg.setAttribute("stroke", pantsColor);
            leg.setAttribute("stroke-width", 16 * scale);
            leg.setAttribute("stroke-linecap", "round");
            g.appendChild(leg);
        });
    }

    // Torso clothing
    if (isWoman) {
        // Girl: Simple dress
        const dress = document.createElementNS("http://www.w3.org/2000/svg", "path");
        const d = `M ${charX - sW / 2} ${shoulderY} L ${charX + sW / 2} ${shoulderY} L ${charX + hipW / 2 + 20 * scale} ${baseHipsY + 30 * scale} L ${charX - hipW / 2 - 20 * scale} ${baseHipsY + 30 * scale} Z`;
        dress.setAttribute("d", d);
        dress.setAttribute("fill", clothingColor);
        dress.setAttribute("stroke", clothingAccent);
        dress.setAttribute("stroke-width", 2);
        g.appendChild(dress);
    } else {
        // Boy: Shirt
        const shirt = document.createElementNS("http://www.w3.org/2000/svg", "path");
        const d = `M ${charX - sW / 2} ${shoulderY} L ${charX + sW / 2} ${shoulderY} L ${charX + hipW / 2} ${baseHipsY} L ${charX - hipW / 2} ${baseHipsY} Z`;
        shirt.setAttribute("d", d);
        shirt.setAttribute("fill", shirtColor);
        shirt.setAttribute("stroke", "#B4BEC8");
        shirt.setAttribute("stroke-width", 2);
        g.appendChild(shirt);
    }

    // === WHITE BODY PARTS (over clothing) ===

    if (!isWoman) {
        // Boy legs (white feet, visible below pants)
        [-1, 1].forEach(side => {
            const lx = charX + side * (hipW / 4);
            const foot = document.createElementNS("http://www.w3.org/2000/svg", "circle");
            foot.setAttribute("cx", lx);
            foot.setAttribute("cy", charY);
            foot.setAttribute("r", 10 * scale);
            foot.setAttribute("fill", "white");
            g.appendChild(foot);
        });
    } else {
        // Girl legs (white, visible below dress)
        [-1, 1].forEach(side => {
            const leg = document.createElementNS("http://www.w3.org/2000/svg", "line");
            leg.setAttribute("x1", charX + side * (hipW / 4));
            leg.setAttribute("y1", baseHipsY + 30 * scale);
            leg.setAttribute("x2", charX + side * (hipW / 4));
            leg.setAttribute("y2", charY);
            leg.setAttribute("stroke", "white");
            leg.setAttribute("stroke-width", 16 * scale);
            leg.setAttribute("stroke-linecap", "round");
            g.appendChild(leg);
        });
    }

    // Arms
    const armRadius = 7 * scale;

    // Left arm (chocolate hand if applicable)
    if (hasChocolate) {
        const lShoulder = [charX - sW / 2, shoulderY + 10];
        const lElbow = [charX - sW / 2 - 10, shoulderY + 40 * scale];
        const lHand = [charX - 20, shoulderY + 60 * scale];

        const arm1 = document.createElementNS("http://www.w3.org/2000/svg", "line");
        arm1.setAttribute("x1", lShoulder[0]);
        arm1.setAttribute("y1", lShoulder[1]);
        arm1.setAttribute("x2", lElbow[0]);
        arm1.setAttribute("y2", lElbow[1]);
        arm1.setAttribute("stroke", "white");
        arm1.setAttribute("stroke-width", armRadius * 2);
        arm1.setAttribute("stroke-linecap", "round");
        g.appendChild(arm1);

        const arm2 = document.createElementNS("http://www.w3.org/2000/svg", "line");
        arm2.setAttribute("x1", lElbow[0]);
        arm2.setAttribute("y1", lElbow[1]);
        arm2.setAttribute("x2", lHand[0]);
        arm2.setAttribute("y2", lHand[1]);
        arm2.setAttribute("stroke", "white");
        arm2.setAttribute("stroke-width", armRadius * 2);
        arm2.setAttribute("stroke-linecap", "round");
        g.appendChild(arm2);
    } else {
        const lArm = document.createElementNS("http://www.w3.org/2000/svg", "line");
        lArm.setAttribute("x1", charX - sW / 2);
        lArm.setAttribute("y1", shoulderY + 10);
        lArm.setAttribute("x2", charX - sW / 2 - 5);
        lArm.setAttribute("y2", shoulderY + 95 * scale);
        lArm.setAttribute("stroke", "white");
        lArm.setAttribute("stroke-width", armRadius * 2);
        lArm.setAttribute("stroke-linecap", "round");
        g.appendChild(lArm);
    }

    // Right arm
    const rArm = document.createElementNS("http://www.w3.org/2000/svg", "line");
    rArm.setAttribute("x1", charX + sW / 2);
    rArm.setAttribute("y1", shoulderY + 10);
    rArm.setAttribute("x2", charX + sW / 2 + 5);
    rArm.setAttribute("y2", shoulderY + 95 * scale);
    rArm.setAttribute("stroke", "white");
    rArm.setAttribute("stroke-width", armRadius * 2);
    rArm.setAttribute("stroke-linecap", "round");
    g.appendChild(rArm);

    // Head
    const head = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    head.setAttribute("cx", charX);
    head.setAttribute("cy", headY);
    head.setAttribute("r", headR);
    head.setAttribute("fill", "white");
    head.setAttribute("stroke", "#eee");
    g.appendChild(head);

    // Face
    [charX - 10 * scale, charX + 10 * scale].forEach(ex => {
        const eye = document.createElementNS("http://www.w3.org/2000/svg", "circle");
        eye.setAttribute("cx", ex);
        eye.setAttribute("cy", headY - 5 * scale);
        eye.setAttribute("r", 3.5);
        eye.setAttribute("fill", "#333");
        g.appendChild(eye);
    });

    const mY = headY + 14 * scale;
    if (expression === 'smile') {
        const mouth = document.createElementNS("http://www.w3.org/2000/svg", "path");
        mouth.setAttribute("d", `M ${charX - 10 * scale} ${mY} Q ${charX} ${mY + 8 * scale} ${charX + 10 * scale} ${mY}`);
        mouth.setAttribute("fill", "none");
        mouth.setAttribute("stroke", "#333");
        mouth.setAttribute("stroke-width", "2");
        g.appendChild(mouth);
    } else {
        const mouth = document.createElementNS("http://www.w3.org/2000/svg", "line");
        mouth.setAttribute("x1", charX - 4);
        mouth.setAttribute("y1", mY + 2);
        mouth.setAttribute("x2", charX + 4);
        mouth.setAttribute("y2", mY + 2);
        mouth.setAttribute("stroke", "#333");
        mouth.setAttribute("stroke-width", "2");
        g.appendChild(mouth);
    }

    if (isWoman) {
        const bowX = charX + 22 * scale, bowY = headY - 25 * scale;
        const leftLoop = document.createElementNS("http://www.w3.org/2000/svg", "ellipse");
        leftLoop.setAttribute("cx", bowX - 7);
        leftLoop.setAttribute("cy", bowY);
        leftLoop.setAttribute("rx", 5);
        leftLoop.setAttribute("ry", 6);
        leftLoop.setAttribute("fill", "hotpink");
        g.appendChild(leftLoop);

        const rightLoop = document.createElementNS("http://www.w3.org/2000/svg", "ellipse");
        rightLoop.setAttribute("cx", bowX + 7);
        rightLoop.setAttribute("cy", bowY);
        rightLoop.setAttribute("rx", 5);
        rightLoop.setAttribute("ry", 6);
        rightLoop.setAttribute("fill", "hotpink");
        g.appendChild(rightLoop);

        const knot = document.createElementNS("http://www.w3.org/2000/svg", "circle");
        knot.setAttribute("cx", bowX);
        knot.setAttribute("cy", bowY);
        knot.setAttribute("r", 4);
        knot.setAttribute("fill", "#c83264");
        g.appendChild(knot);
    }

    // Draw chocolate if in hand
    if (hasChocolate) {
        const lHand = [charX - 20, shoulderY + 60 * scale];
        g.appendChild(drawChocolate(lHand[0], lHand[1]));
    }

    return g;
}

function animate(time) {
    if (isPaused) {
        requestAnimationFrame(animate);
        return;
    }
    const adjustedTime = time - totalPausedTime;
    const elapsed = adjustedTime - sceneStartTime;
    const scene = config.scenes[currentIdx];
    const breath = Math.sin(adjustedTime * 0.002) * 3;
    svg.innerHTML = '';

    if (scene.type === 'theme' || scene.type === 'intro' || scene.type === 'final') {
        // Text only scenes - no characters
    } else {
        const bx = 1280 * 0.42, gx = 1280 * 0.58;
        const chocState = scene.chocolate || 'none';

        if (scene.boy) {
            const hasChoc = ['in_hand', 'looking'].includes(chocState);
            svg.appendChild(drawHuman(bx + 50, 720 * 0.8, false, 'neutral', breath, hasChoc));
        } else if (scene.girl) {
            svg.appendChild(drawHuman(gx - 50, 720 * 0.8, true, 'neutral', breath));
        } else if (scene.both) {
            const hasChoc = chocState === 'offering';
            svg.appendChild(drawHuman(bx, 720 * 0.8, false, 'neutral', breath, hasChoc));

            const girlHasChoc = chocState === 'received';
            const girlExpr = girlHasChoc ? 'smile' : 'neutral';
            svg.appendChild(drawHuman(gx, 720 * 0.8, true, girlExpr, breath, girlHasChoc));

            // Chocolate transfer animation
            if (chocState === 'transferring') {
                const progress = Math.min(1.0, elapsed / 3000);
                const boyChocX = bx - 20, boyChocY = 720 * 0.8 - 140;
                const girlChocX = gx - 20, girlChocY = 720 * 0.8 - 140;

                const chocX = boyChocX + (girlChocX - boyChocX) * progress;
                const chocY = boyChocY + (girlChocY - boyChocY) * progress;

                svg.appendChild(drawChocolate(chocX, chocY));
            }
        }
    }
    requestAnimationFrame(animate);
}

function playScene(idx) {
    if (idx >= config.scenes.length) {
        subtitleBox.innerText = 'Chocolate Day';
        subtitleBox.classList.add('intro-text');
        setTimeout(() => overlay.style.display = 'flex', 4000);
        return;
    }
    currentIdx = idx;
    sceneStartTime = performance.now() - totalPausedTime;
    const scene = config.scenes[idx];
    subtitleBox.innerText = scene.text;

    if (scene.type === 'theme' || scene.type === 'intro' || scene.type === 'final') {
        subtitleBox.classList.add('intro-text');
    } else {
        subtitleBox.classList.remove('intro-text');
    }
    subtitleBox.classList.add('visible');

    let duration;
    if (scene.type === 'theme' || scene.type === 'intro' || scene.type === 'final') {
        duration = 5000;
    } else if (scene.silent) {
        duration = 4000;  // Silent transfer scene
    } else if (scene.vo) {
        currentAudio = new Audio(scene.vo);
        currentAudio.play();
        currentAudio.onended = () => {
            setTimeout(() => {
                if (isPaused) {
                    const check = setInterval(() => {
                        if (!isPaused) {
                            clearInterval(check);
                            finishScene();
                        }
                    }, 100);
                } else finishScene();
            }, 2500);
        };
        return;  // Audio will trigger next scene
    } else {
        duration = 5000;
    }

    setTimeout(() => finishScene(), duration);

    function finishScene() {
        subtitleBox.classList.remove('visible');
        setTimeout(() => playScene(idx + 1), 2500);
    }
}

window.addEventListener('keydown', (e) => {
    if (e.key === ' ' || e.code === 'Space') {
        e.preventDefault();
        isPaused = !isPaused;
        if (isPaused) {
            pauseStartTime = performance.now();
            if (currentAudio) currentAudio.pause();
        } else {
            totalPausedTime += (performance.now() - pauseStartTime);
            if (currentAudio) currentAudio.play();
        }
    }
});

startBtn.addEventListener('click', () => {
    overlay.style.opacity = '0';
    setTimeout(() => {
        overlay.style.display = 'none';
        requestAnimationFrame(animate);
        playScene(0);
    }, 1500);
});
