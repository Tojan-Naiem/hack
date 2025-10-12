const spaceMap = document.getElementById('space-map');
        let asteroidInterval;
        let currentPosition = { x: 50, y: 150 };
        let isMoving = false;
        let timeLeft = 30; // seconds - simulation for 30 days

        // Initialize Earth and initial asteroid
        function initializeSimulation() {
            // Add Earth
            const earth = document.createElement('div');
            earth.className = 'earth';
            earth.id = 'earth';
            spaceMap.appendChild(earth);

            // Add asteroid
            const asteroid = document.createElement('div');
            asteroid.className = 'asteroid';
            asteroid.id = 'asteroid';
            asteroid.style.left = currentPosition.x + 'px';
            asteroid.style.top = currentPosition.y + 'px';
            spaceMap.appendChild(asteroid);

            // Remove trajectory - not needed

            updateStatus('Waiting to Start', '--', '--', '--');
            updateCountdown();
        }

        // بدء الحركة التلقائية
        function startAutoMovement() {
            if (isMoving) return;
            
            isMoving = true;
            updateStatus('Asteroid Moving', 'Collision Course', 'High', '30 days');
            
            asteroidInterval = setInterval(() => {
                if (timeLeft <= 0) {
                    impact();
                    return;
                }
                
                timeLeft--;
                currentPosition.x += 20;
                currentPosition.y += 3;
                
                updateAsteroidPosition();
                updateCountdown();
                updateDistance();
                
            }, 100); // Update every 100 milliseconds
        }

        // تحديث موقع الكويكب
        function updateAsteroidPosition() {
            const asteroid = document.getElementById('asteroid');
            if (asteroid) {
                asteroid.style.left = currentPosition.x + 'px';
                asteroid.style.top = currentPosition.y + 'px';
                
                // تأثير الاهتزاز مع الاقتراب
                if (timeLeft < 10) {
                    asteroid.style.transform = `translate(${Math.random() * 4 - 2}px, ${Math.random() * 4 - 2}px)`;
                }
            }
        }

        // Remove trajectory function - not needed

        // تحديث العد التنازلي
        function updateCountdown() {
            const days = Math.floor(timeLeft / 3);
            const hours = (timeLeft % 3) * 8;
            document.getElementById('countdown').textContent = 
                `${days} days ${hours} hours`;
            document.getElementById('time-left').textContent = 
                `${days} days ${hours} hours`;
        }

        // Update distance
        function updateDistance() {
            const earthX = 800, earthY = 450;
            const dx = earthX - currentPosition.x;
            const dy = earthY - currentPosition.y;
            const distance = Math.sqrt(dx * dx + dy * dy);
            const realDistance = Math.max(0, (distance / 750) * 400000).toFixed(0); // simulation for 400,000 km
            
            document.getElementById('distance-left').textContent = 
                `${realDistance} thousand km`;
            
            // Update speed (increases with proximity)
            const speed = 16 + (30 - timeLeft) * 0.5;
            document.getElementById('current-speed').textContent = 
                `${speed.toFixed(1)} km/s`;
        }

        // تفعيل الدفاع
        function activateDefense(type) {
            if (!isMoving) return;
            
            clearInterval(asteroidInterval);
            isMoving = false;
            
            let status, danger, energy;
            
            switch(type) {
                case 'success':
                    // Successfully change course
                    currentPosition.y -= 100;
                    status = 'Success - Course Changed';
                    danger = 'Low';
                    energy = '0 MT';
                    break;
                    
                case 'partial':
                    // Damage mitigation
                    currentPosition.x += 50;
                    status = 'Partial - Limited Damage';
                    danger = 'Medium';
                    energy = '0.08 MT';
                    createExplosion(currentPosition.x, currentPosition.y);
                    break;
                    
                case 'destroy':
                    // Asteroid destruction
                    status = 'Success - Asteroid Destroyed';
                    danger = 'None';
                    energy = '0.01 MT';
                    createFragments();
                    document.getElementById('asteroid').style.display = 'none';
                    break;
            }
            
            updateAsteroidPosition();
            updateStatus(status, 'Collision avoided Successfully!', danger, energy);
        }

        // Impact
        function impact() {
            clearInterval(asteroidInterval);
            createExplosion(currentPosition.x, currentPosition.y);
            updateStatus('Direct Impact', 'Populated Area', 'Catastrophic', '0.24 MT');
            document.getElementById('asteroid').style.display = 'none';
        }

        // Create explosion
        function createExplosion(x, y) {
            const explosion = document.createElement('div');
            explosion.className = 'explosion';
            explosion.style.left = (x - 50) + 'px';
            explosion.style.top = (y - 50) + 'px';
            spaceMap.appendChild(explosion);

            setTimeout(() => explosion.remove(), 500);
        }

        // Create fragments
        function createFragments() {
            for(let i = 0; i < 15; i++) {
                const fragment = document.createElement('div');
                fragment.className = 'fragments';
                fragment.style.left = (currentPosition.x + Math.random() * 100 - 50) + 'px';
                fragment.style.top = (currentPosition.y + Math.random() * 100 - 50) + 'px';
                spaceMap.appendChild(fragment);
            }
        }

        // تحديث الحالة
        function updateStatus(status, impact, danger, energy) {
            document.getElementById('mission-status').textContent = status;
            document.getElementById('impact-point').textContent = impact;
            document.getElementById('danger-level').textContent = danger;
        }

        // إعادة التعيين
        function resetSimulation() {
            clearInterval(asteroidInterval);
            isMoving = false;
            currentPosition = { x: 50, y: 150 };
            timeLeft = 30;
            
            document.querySelectorAll('#asteroid, .fragments, .explosion').forEach(el => el.remove());
            initializeSimulation();
        }

        // التهيئة الأولية
        initializeSimulation();