const config = {
    scenes: [
        { type: 'theme', text: 'Rose Day showed intention.\nPropose Day brings clarity and courage.' },
        { vo: 'assets/audio/h_sc1.mp3', text: 'After the rose was given, nothing was said.\nBut something had already been understood.' },
        { vo: 'assets/audio/h_sc2.mp3', text: 'I’ve never known how to show love loudly.\nWords were the only place I felt honest.', boy: true },
        { vo: 'assets/audio/h_sc3.mp3', text: 'She noticed the difference between silence and hesitation.\nThis was not hesitation.', girl: true },
        {
            vo: 'assets/audio/h_sc4.mp3', text: 'I don\'t know how to impress you.\nBut I don\'t want to stand in your way; I want to stand with you, when you\'re ready.', both: true
        },
        { vo: 'assets/audio/h_sc5.mp3', text: 'If one day you choose forever,\nI want to choose it with you.', both: true },
        { vo: 'assets/audio/h_sc6.mp3', text: 'She didn’t answer him.\nShe let him know he was heard.', both: true, smile: true, step: true },
        { vo: 'assets/audio/h_sc7.mp3', text: 'Propose Day is not about hearing yes.\nIt is about being brave enough to mean it.', type: 'final_resolution' }
    ],
    bgColor: '#D3D3D3', textColor: '#2D2D2D'
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

function drawThoughtCloud(svg, x, y, scale = 1.0) {
    const g = document.createElementNS("http://www.w3.org/2000/svg", "g");

    // Main cloud circles
    const circles = [
        { cx: x, cy: y, r: 18 * scale },
        { cx: x - 15 * scale, cy: y - 5, r: 14 * scale },
        { cx: x + 15 * scale, cy: y - 5, r: 14 * scale },
        { cx: x, cy: y - 15, r: 12 * scale }
    ];

    circles.forEach(c => {
        const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
        circle.setAttribute("cx", c.cx); circle.setAttribute("cy", c.cy);
        circle.setAttribute("r", c.r);
        circle.setAttribute("fill", "white"); circle.setAttribute("stroke", "#ccc");
        g.appendChild(circle);
    });

    // Small bubbles connecting to head
    [[x - 10, y + 25, 5 * scale], [x - 15, y + 35, 3 * scale]].forEach(b => {
        const bubble = document.createElementNS("http://www.w3.org/2000/svg", "circle");
        bubble.setAttribute("cx", b[0]); bubble.setAttribute("cy", b[1]);
        bubble.setAttribute("r", b[2]);
        bubble.setAttribute("fill", "white"); bubble.setAttribute("stroke", "#ccc");
        g.appendChild(bubble);
    });

    return g;
}

function drawHuman(x, y, isWoman = false, expression = 'neutral', breath = 0, noteState = 'hidden', step = 0, talking = false) {
    const scale = isWoman ? 0.78 : 0.95;
    const charX = x + (isWoman ? -step : 0);
    const charY = y - (isWoman ? breath * 0.3 : breath * 0.4);
    const g = document.createElementNS("http://www.w3.org/2000/svg", "g");

    const shadow = document.createElementNS("http://www.w3.org/2000/svg", "ellipse");
    shadow.setAttribute("cx", charX); shadow.setAttribute("cy", y + 5);
    shadow.setAttribute("rx", 55 * scale); shadow.setAttribute("ry", 10);
    shadow.setAttribute("fill", "rgba(0,0,0,0.1)");
    g.appendChild(shadow);

    const headR = 30 * scale;
    const sW = (isWoman ? 52 : 68) * scale;
    const torsoH = (110 + breath) * scale;
    const hipW = (isWoman ? 56 : 48) * scale;
    const legH = 120 * scale;
    const baseHipsY = y - legH;
    const shoulderY = baseHipsY - torsoH;

    [-1, 1].forEach(side => {
        const lx = charX + side * (hipW / 4);
        const leg = document.createElementNS("http://www.w3.org/2000/svg", "line");
        leg.setAttribute("x1", lx); leg.setAttribute("y1", baseHipsY);
        leg.setAttribute("x2", lx); leg.setAttribute("y2", y);
        leg.setAttribute("stroke", "white"); leg.setAttribute("stroke-width", 16 * scale);
        leg.setAttribute("stroke-linecap", "round");
        g.appendChild(leg);
    });

    const torso = document.createElementNS("http://www.w3.org/2000/svg", "path");
    const d = `M ${charX - sW / 2} ${shoulderY} L ${charX + sW / 2} ${shoulderY} L ${charX + hipW / 2} ${baseHipsY} L ${charX - hipW / 2} ${baseHipsY} Z`;
    torso.setAttribute("d", d); torso.setAttribute("fill", "white"); torso.setAttribute("stroke", "#eee");
    g.appendChild(torso);

    const lArm = document.createElementNS("http://www.w3.org/2000/svg", "path");
    if (noteState !== 'hidden' && !isWoman) {
        const handX = charX - 20 * scale, handY = baseHipsY - 60 * scale;
        lArm.setAttribute("d", `M ${charX - sW / 2} ${shoulderY + 10} Q ${charX - 30 * scale} ${shoulderY + 40 * scale} ${handX} ${handY}`);
        const nw = 25 * scale, nh = 18 * scale;
        const note = document.createElementNS("http://www.w3.org/2000/svg", "rect");
        note.setAttribute("x", handX - nw / 2); note.setAttribute("y", handY - nh / 2);
        note.setAttribute("width", nw); note.setAttribute("height", nh);
        note.setAttribute("fill", "white"); note.setAttribute("stroke", "#ccc");
        g.appendChild(note);
    } else {
        lArm.setAttribute("d", `M ${charX - sW / 2} ${shoulderY + 10} L ${charX - sW / 2 - 5} ${shoulderY + 95 * scale}`);
    }
    lArm.setAttribute("fill", "none"); lArm.setAttribute("stroke", "white"); lArm.setAttribute("stroke-width", 14 * scale); lArm.setAttribute("stroke-linecap", "round");
    g.appendChild(lArm);

    const armR = document.createElementNS("http://www.w3.org/2000/svg", "line");
    armR.setAttribute("x1", charX + sW / 2); armR.setAttribute("y1", shoulderY + 10);
    armR.setAttribute("x2", charX + sW / 2 + 5); armR.setAttribute("y2", shoulderY + 95 * scale);
    armR.setAttribute("stroke", "white"); armR.setAttribute("stroke-width", 14 * scale); armR.setAttribute("stroke-linecap", "round");
    g.appendChild(armR);

    const headY = shoulderY - 10 * scale - headR;
    const head = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    head.setAttribute("cx", charX); head.setAttribute("cy", headY);
    head.setAttribute("r", headR); head.setAttribute("fill", "white"); head.setAttribute("stroke", "#eee");
    g.appendChild(head);

    [charX - 10 * scale, charX + 10 * scale].forEach(ex => {
        const eye = document.createElementNS("http://www.w3.org/2000/svg", "circle");
        eye.setAttribute("cx", ex); eye.setAttribute("cy", headY - 5 * scale);
        eye.setAttribute("r", 3.5); eye.setAttribute("fill", "#333");
        g.appendChild(eye);
    });

    const mY = headY + 14 * scale;
    if (talking) {
        const talkH = 4 + Math.sin(performance.now() * 0.02) * 4;
        const mouth = document.createElementNS("http://www.w3.org/2000/svg", "ellipse");
        mouth.setAttribute("cx", charX); mouth.setAttribute("cy", mY);
        mouth.setAttribute("rx", 4); mouth.setAttribute("ry", Math.max(1, talkH / 2));
        mouth.setAttribute("fill", "#333");
        g.appendChild(mouth);
    } else if (expression === 'smile') {
        const mouth = document.createElementNS("http://www.w3.org/2000/svg", "path");
        mouth.setAttribute("d", `M ${charX - 10 * scale} ${mY} Q ${charX} ${mY + 8 * scale} ${charX + 10 * scale} ${mY}`);
        mouth.setAttribute("fill", "none"); mouth.setAttribute("stroke", "#333"); mouth.setAttribute("stroke-width", "2");
        g.appendChild(mouth);
    } else {
        const mouth = document.createElementNS("http://www.w3.org/2000/svg", "line");
        mouth.setAttribute("x1", charX - 4); mouth.setAttribute("y1", mY + 2);
        mouth.setAttribute("x2", charX + 4); mouth.setAttribute("y2", mY + 2);
        mouth.setAttribute("stroke", "#333"); mouth.setAttribute("stroke-width", "2");
        g.appendChild(mouth);
    }

    if (isWoman) {
        // Ribbon bow on the side of her head
        const bowX = charX + 22 * scale, bowY = headY - 25 * scale;
        // Left loop
        const leftLoop = document.createElementNS("http://www.w3.org/2000/svg", "ellipse");
        leftLoop.setAttribute("cx", bowX - 7); leftLoop.setAttribute("cy", bowY);
        leftLoop.setAttribute("rx", 5); leftLoop.setAttribute("ry", 6);
        leftLoop.setAttribute("fill", "hotpink");
        g.appendChild(leftLoop);
        // Right loop
        const rightLoop = document.createElementNS("http://www.w3.org/2000/svg", "ellipse");
        rightLoop.setAttribute("cx", bowX + 7); rightLoop.setAttribute("cy", bowY);
        rightLoop.setAttribute("rx", 5); rightLoop.setAttribute("ry", 6);
        rightLoop.setAttribute("fill", "hotpink");
        g.appendChild(rightLoop);
        // Center knot
        const knot = document.createElementNS("http://www.w3.org/2000/svg", "circle");
        knot.setAttribute("cx", bowX); knot.setAttribute("cy", bowY);
        knot.setAttribute("r", 4); knot.setAttribute("fill", "#c83264");
        g.appendChild(knot);
    }

    return g;
}

function drawHumanFront(x, y, isWoman = false, expression = 'neutral', breath = 0, walkPhase = 0) {
    const scale = isWoman ? 0.78 : 0.95;
    const g = document.createElementNS("http://www.w3.org/2000/svg", "g");

    const headR = 30 * scale;
    const torsoH = (110 + breath) * scale;
    const shoulderW = (isWoman ? 52 : 68) * scale;
    const hipW = (isWoman ? 56 : 48) * scale;
    const legH = 120 * scale;
    const baseHipsY = y - legH;
    const shoulderY = baseHipsY - torsoH;
    const headY = shoulderY - 10 * scale - headR;

    // Shadow
    const shadow = document.createElementNS("http://www.w3.org/2000/svg", "ellipse");
    shadow.setAttribute("cx", x); shadow.setAttribute("cy", y + 5);
    shadow.setAttribute("rx", 55 * scale); shadow.setAttribute("ry", 10);
    shadow.setAttribute("fill", "rgba(0,0,0,0.1)");
    g.appendChild(shadow);

    // Walking leg animation
    const legOffset = Math.sin(walkPhase) * 15;
    const leftKneeX = x - hipW / 4 + legOffset;
    const rightKneeX = x + hipW / 4 - legOffset;
    const leftFootX = x - hipW / 4 + legOffset * 1.5;
    const rightFootX = x + hipW / 4 - legOffset * 1.5;
    const kneeY = (baseHipsY + y) / 2;
    const legRadius = 8 * scale;

    // Legs with walking motion
    [[x - hipW / 4, baseHipsY, leftKneeX, kneeY], [leftKneeX, kneeY, leftFootX, y],
    [x + hipW / 4, baseHipsY, rightKneeX, kneeY], [rightKneeX, kneeY, rightFootX, y]].forEach(l => {
        const leg = document.createElementNS("http://www.w3.org/2000/svg", "line");
        leg.setAttribute("x1", l[0]); leg.setAttribute("y1", l[1]);
        leg.setAttribute("x2", l[2]); leg.setAttribute("y2", l[3]);
        leg.setAttribute("stroke", "white"); leg.setAttribute("stroke-width", legRadius * 2);
        leg.setAttribute("stroke-linecap", "round");
        g.appendChild(leg);
    });

    // Torso (front view)
    const torso = document.createElementNS("http://www.w3.org/2000/svg", "path");
    const d = `M ${x - shoulderW / 2} ${shoulderY} L ${x + shoulderW / 2} ${shoulderY} L ${x + hipW / 2} ${baseHipsY} L ${x - hipW / 2} ${baseHipsY} Z`;
    torso.setAttribute("d", d); torso.setAttribute("fill", "white"); torso.setAttribute("stroke", "#eee");
    g.appendChild(torso);

    // Arms (hanging down)
    const armRadius = 7 * scale;
    [[x - shoulderW / 2, shoulderY + 10, x - shoulderW / 2 - 5, shoulderY + 90 * scale],
    [x + shoulderW / 2, shoulderY + 10, x + shoulderW / 2 + 5, shoulderY + 90 * scale]].forEach(a => {
        const arm = document.createElementNS("http://www.w3.org/2000/svg", "line");
        arm.setAttribute("x1", a[0]); arm.setAttribute("y1", a[1]);
        arm.setAttribute("x2", a[2]); arm.setAttribute("y2", a[3]);
        arm.setAttribute("stroke", "white"); arm.setAttribute("stroke-width", armRadius * 2);
        arm.setAttribute("stroke-linecap", "round");
        g.appendChild(arm);
    });

    // Head (front view)
    const head = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    head.setAttribute("cx", x); head.setAttribute("cy", headY);
    head.setAttribute("r", headR); head.setAttribute("fill", "white"); head.setAttribute("stroke", "#eee");
    g.appendChild(head);

    // Face (front view - symmetrical)
    const eyeX = 12 * scale;
    const eyeY = headY - 8 * scale;
    [x - eyeX, x + eyeX].forEach(ex => {
        const eye = document.createElementNS("http://www.w3.org/2000/svg", "circle");
        eye.setAttribute("cx", ex); eye.setAttribute("cy", eyeY);
        eye.setAttribute("r", 3.5); eye.setAttribute("fill", "#333");
        g.appendChild(eye);
    });

    const mY = headY + headR / 2 - 5;
    if (expression === 'smile') {
        const mouth = document.createElementNS("http://www.w3.org/2000/svg", "path");
        mouth.setAttribute("d", `M ${x - 12} ${mY} Q ${x} ${mY + 10} ${x + 12} ${mY}`);
        mouth.setAttribute("fill", "none"); mouth.setAttribute("stroke", "#333"); mouth.setAttribute("stroke-width", "2");
        g.appendChild(mouth);
    } else {
        const mouth = document.createElementNS("http://www.w3.org/2000/svg", "line");
        mouth.setAttribute("x1", x - 6); mouth.setAttribute("y1", mY);
        mouth.setAttribute("x2", x + 6); mouth.setAttribute("y2", mY);
        mouth.setAttribute("stroke", "#333"); mouth.setAttribute("stroke-width", "2");
        g.appendChild(mouth);
    }

    // Bow (front view - centered on top)
    if (isWoman) {
        const bowX = x, bowY = headY - headR - 5;
        const leftLoop = document.createElementNS("http://www.w3.org/2000/svg", "ellipse");
        leftLoop.setAttribute("cx", bowX - 7); leftLoop.setAttribute("cy", bowY);
        leftLoop.setAttribute("rx", 5); leftLoop.setAttribute("ry", 6);
        leftLoop.setAttribute("fill", "hotpink");
        g.appendChild(leftLoop);

        const rightLoop = document.createElementNS("http://www.w3.org/2000/svg", "ellipse");
        rightLoop.setAttribute("cx", bowX + 7); rightLoop.setAttribute("cy", bowY);
        rightLoop.setAttribute("rx", 5); rightLoop.setAttribute("ry", 6);
        rightLoop.setAttribute("fill", "hotpink");
        g.appendChild(rightLoop);

        const knot = document.createElementNS("http://www.w3.org/2000/svg", "circle");
        knot.setAttribute("cx", bowX); knot.setAttribute("cy", bowY);
        knot.setAttribute("r", 4); knot.setAttribute("fill", "#c83264");
        g.appendChild(knot);
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

    if (scene.type === 'theme' || scene.type === 'final_resolution') {
        // No characters
    } else {
        const bx = 1280 * 0.42, gx = 1280 * 0.58;
        const adjustedTime = time - totalPausedTime;
        const elapsed = adjustedTime - sceneStartTime;

        if (scene.boy) {
            let boyTalking = false;  // Scene 2 is thoughts, not speech
            svg.appendChild(drawHuman(bx + 50, 720 * 0.8, false, 'neutral', breath, 'folded', 0, boyTalking));
        } else if (scene.girl) {
            svg.appendChild(drawHuman(gx - 50, 720 * 0.8, true, 'neutral', breath));
        } else if (scene.both) {
            // Scene 6: Girl turns away (leaving but smiling)
            let step = 0;
            if (currentIdx === 6) {
                step = -Math.min(80, elapsed * 0.016); // Negative = moving away, increased distance
            } else if (currentIdx > 6) {
                step = -80; // Keep distance
            }

            let noteProgress = 0;
            if (currentIdx === 4) {
                noteProgress = Math.min(1.0, elapsed / 4000);
            } else if (currentIdx > 4) {
                noteProgress = 1.0;
            }

            let femaleExpression = 'neutral';
            if (currentIdx === 6) femaleExpression = 'smile';  // Only smile when leaving in Scene 6

            let boyTalking = (currentIdx === 4 || currentIdx === 5) && currentAudio && !currentAudio.paused && !currentAudio.ended;

            // Scene 6: Girl faces camera and walks away with smile
            if (currentIdx === 6) {
                // Girl walks toward camera (away from boy) - she actually moves
                const walkDistance = Math.min(80, (elapsed / 5000) * 80);  // Distance she moves away
                const walkPhase = (elapsed / 500) * Math.PI;  // Walking animation speed
                svg.appendChild(drawHuman(bx, 720 * 0.8, false, 'neutral', breath, (noteProgress < 0.2 ? 'folded' : 'hidden'), 0, boyTalking));
                // Girl moves toward right side of screen as she walks toward camera
                svg.appendChild(drawHumanFront(gx + walkDistance, 720 * 0.8, true, femaleExpression, breath, walkPhase));
            } else {
                // Normal side view for other scenes
                svg.appendChild(drawHuman(bx, 720 * 0.8, false, 'neutral', breath, (noteProgress < 0.2 ? 'folded' : 'hidden'), 0, boyTalking));
                svg.appendChild(drawHuman(gx, 720 * 0.8, true, femaleExpression, breath, 'hidden', step));
            }

            // Floating Note
            if (noteProgress >= 0.2) {
                const boyNoteX = bx + 20, boyNoteY = (720 * 0.8) - 140;
                const girlNoteX = (gx - step) - 30, girlNoteY = (720 * 0.8) - 130;

                let nx, ny;
                // In Scene 6, note moves with the girl
                if (currentIdx === 6) {
                    const walkDistance = Math.min(80, (elapsed / 5000) * 80);
                    nx = gx + walkDistance - 30;
                    ny = girlNoteY;
                } else {
                    nx = boyNoteX + (girlNoteX - boyNoteX) * noteProgress;
                    ny = boyNoteY + (girlNoteY - boyNoteY) * noteProgress;
                }

                const scale = 0.78;
                const nw = 25 * scale, nh = 18 * scale;
                const note = document.createElementNS("http://www.w3.org/2000/svg", "rect");
                note.setAttribute("x", nx - nw / 2); note.setAttribute("y", ny - nh / 2);
                note.setAttribute("width", nw); note.setAttribute("height", nh);
                note.setAttribute("fill", "white"); note.setAttribute("stroke", "#ccc");
                svg.appendChild(note);
            }
        }
    }
    requestAnimationFrame(animate);
}

function playScene(idx) {
    if (idx >= config.scenes.length) {
        subtitleBox.innerText = 'Propose Day';
        subtitleBox.classList.add('intro-text');
        setTimeout(() => overlay.style.display = 'flex', 4000);
        return;
    }
    currentIdx = idx;
    sceneStartTime = performance.now() - totalPausedTime;
    const scene = config.scenes[idx];
    subtitleBox.innerText = scene.text;
    if (scene.type === 'theme') subtitleBox.classList.add('intro-text');
    else subtitleBox.classList.remove('intro-text');
    subtitleBox.classList.add('visible');

    if (scene.vo) {
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
            }, 1000);
        };
    } else {
        setTimeout(() => finishScene(), 5000);
    }

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
