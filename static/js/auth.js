document.addEventListener("DOMContentLoaded", () => {
    const loginForm = document.getElementById("login-form");
    const regForm   = document.getElementById("register-form");
    const errorBox  = document.getElementById("error-box");
    const errorText = document.getElementById("error-text");

    function showError(msg) {
        if (!errorBox) return;
        errorText.innerText = msg;
        errorBox.classList.remove("hidden");
        setTimeout(() => errorBox.scrollIntoView({ behavior: 'smooth' }), 100);
    }

    function clearError() {
        if (errorBox) errorBox.classList.add("hidden");
    }

    // ── LOGIN LOGIC ─────────────────────────────────────────────
    if (loginForm) {
        loginForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            clearError();
            
            const email = document.getElementById("email").value;
            const password = document.getElementById("password").value;

            try {
                // 1. Попытка локального входа (подходит для офлайн/mock режима)
                const localRes = await fetch("/api/login", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ email, password })
                });
                const localData = await localRes.json();
                if (localData.success) {
                    location.href = localData.redirect || '/';
                    return;
                }
                
                // 2. Если локальный вход не удался с ошибкой, отличной от "Не найден", пробуем Firebase (для онлайн режима)
                if (localData.error && localData.error.includes("Пользователь с таким email не найден")) {
                    try {
                        const cred = await firebase.auth().signInWithEmailAndPassword(email, password);
                        const idToken = await cred.user.getIdToken();

                        const res = await fetch("/api/login", {
                            method: "POST",
                            headers: { "Content-Type": "application/json" },
                            body: JSON.stringify({ idToken })
                        });
                        const data = await res.json();
                        if (data.success) {
                            location.href = data.redirect || '/';
                        } else {
                            showError(data.error);
                            firebase.auth().signOut();
                        }
                    } catch (fbErr) {
                        showError("Неверный логин или пароль");
                    }
                } else {
                    showError(localData.error || "Неверный логин или пароль");
                }
            } catch (err) {
                showError("Ошибка сети при входе");
            }
        });
    }

    // ── REGISTER LOGIC (COMMON FOR ALL 3 PAGES) ─────────────────
    if (regForm) {
        regForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            clearError();
            
            const role = regForm.querySelector('input[name="role"]').value;
            const name = document.getElementById("name").value;
            const email = document.getElementById("email").value;
            const password = document.getElementById("password").value;
            const profession = document.getElementById("profession").value;
            
            // Optional fields based on role
            const curator_id = document.getElementById("curator_id")?.value || null;
            const child_id = document.getElementById("child_id")?.value || null;

            if (!name || !email || !password) {
                showError("Пожалуйста, заполните все поля");
                return;
            }

            try {
                let uid = "local_uid_" + Math.random().toString(36).substr(2, 9);
                try {
                    // 1. Попытка регистрации в Firebase (для онлайн режима)
                    const cred = await firebase.auth().createUserWithEmailAndPassword(email, password);
                    uid = cred.user.uid;
                } catch (fbErr) {
                    console.log("Firebase registration skipped/failed, proceeding locally:", fbErr);
                }

                // 2. Flask DB Save
                const res = await fetch("/api/register", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ 
                        uid, role, name, profession, email, password,
                        curator_id, child_id 
                    })
                });
                const data = await res.json();
                
                if (data.success) {
                    // Симулируем локальный вход сразу после регистрации
                    await fetch("/api/login", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ email, password })
                    });

                    // Redirect based on role
                    if (role === 'student') location.href = '/student';
                    else if (role === 'curator') location.href = '/curator';
                    else location.href = '/auth'; // Parent login after register
                } else {
                    showError(data.error);
                }
            } catch (err) {
                showError(err.message || "Ошибка при регистрации");
            }
        });
    }
});
