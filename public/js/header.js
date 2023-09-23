const token = localStorage.getItem("token");

//----------------------
// 打開關閉登入註冊
//----------------------
const showModalButton = document.getElementById("show-login-button");
const closeloginButton = document.getElementById("close-login");
const loginForm = document.getElementById("login-form");
const registerPageButton = document.querySelector(".login-form-register");
const registerForm = document.querySelector(".register-form");
const loginPageButton = document.querySelector(".register-form-login");
const closeregisterButton = document.getElementById("close-register");

// showModalButton.addEventListener("click", () => {
//     loginForm.style.display = "flex";
// });

closeloginButton.addEventListener("click", () => {

    loginForm.style.display = "none";
});
closeregisterButton.addEventListener("click", () => {
    registerMessage.textContent = "";
    registerForm.style.display = "none";
});
registerPageButton.addEventListener("click", () => {
    loginForm.style.display = "none";
    registerForm.style.display = "flex";
});
loginPageButton.addEventListener("click", () => {
    registerForm.style.display = "none";
    loginForm.style.display = "flex";

});

//----------------------
// 會員註冊
//----------------------
const registerInputName = document.getElementById("register-form-input-name");
const registerInputEmail = document.getElementById("register-form-input-email");
const registerInputPassword = document.getElementById("register-form-input-password");
const registerBtn = document.getElementById("register-form-button");
const registerMessage = document.getElementById("register-message");


registerBtn.addEventListener("click", async (e) => {
    e.preventDefault();
    const name = registerInputName.value;
    const email = registerInputEmail.value;
    const password = registerInputPassword.value;

    if (!email || !name || !password) {
        console.log("註冊資料填寫不完全");
        registerMessage.textContent = "請填寫完整資訊";
        registerMessage.style.color = "red";
        return;
    }
    if (isEmailValid(email)) {
        console.log("電子郵件格式正確");

    } else {
        console.log("電子郵件格式不正確");
        registerMessage.textContent = "電子郵件格式不正確";
        registerMessage.style.color = "red";
        return;
    }
    console.log("info:name:", name, ",email:", email, ",password:", password);

    const response = await fetch("/api/user", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            name: name,
            email: email,
            password: password,
        }),
    });
    const result = await response.json();
    console.log("result:", result);

    if ("ok" in result) {
        console.log("result is ok");
        registerMessage.style.color = "green";
        registerMessage.textContent = "註冊成功，請登入系統";
        registerInputName.value = "";
        registerInputEmail.value = "";
        registerInputPassword.value = "";
    } else if ("error" in result) {
        console.log("result is error");
        registerMessage.style.color = "red";
        console.log(result.message);
        registerMessage.textContent = result.message;;
        // registerInputName.value = "";
        // registerInputEmail.value = "";
        // registerInputPassword.value = "";
    }
    // else {
    //     registerMessage.style.color = "red";
    //     registerMessage.textContent = "伺服器內部錯誤";
    //     registerInputName.value = "";
    //     registerInputEmail.value = "";
    //     registerInputPassword.value = "";
    // }
})

//----------------------
// 會員登入
//----------------------
const loginInputEmail = document.getElementById("login-form-input-email");
const loginInputPassword = document.getElementById("login-form-input-password");
const loginBtn = document.getElementById("login-form-button");
const loginMessage = document.getElementById("login-message");

loginBtn.addEventListener("click", async (e) => {
    e.preventDefault();
    const email = loginInputEmail.value;
    const password = loginInputPassword.value;
    if (!email || !password) {
        console.log("登入資料填寫不完全");
        loginMessage.textContent = "請填寫完整資訊";
        loginMessage.style.color = "red";
        return;
    }
    if (isEmailValid(email)) {
        console.log("電子郵件格式正確");

    } else {
        console.log("電子郵件格式不正確");
        loginMessage.textContent = "電子郵件格式不正確";
        loginMessage.style.color = "red";
        return;
    }
    console.log("info:", ",email:", email, ",password:", password);
    const response = await fetch("/api/user/auth", {
        method: "PUT",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            email: email,
            password: password,
        }),
    });
    const result = await response.json();
    console.log("result:", result);
    if ("token" in result) {
        console.log("result is ok");
        localStorage.setItem("token", result.token);
        loginMessage.style.color = "green";
        loginMessage.textContent = "登入成功";
        loginInputEmail.value = "";
        loginInputPassword.value = "";
        window.location.reload();
    }
    else if ("error" in result) {
        console.log("result is error:", result);
        loginMessage.style.color = "red";
        loginMessage.textContent = result["message"];
        loginInputEmail.value = "";
        loginInputPassword.value = "";
    }
})

//----------------------
// 會員狀態
//----------------------
userStatus();
async function userStatus() {
    if (token) {
        const response = await fetch("/api/user/auth", {
            method: "GET",
            headers: {
                Authorization: "Bearer " + token,
            },
        });
        const data = await response.json();
        userData = data["data"];
    } else {
        const response = await fetch("/api/user/auth");
        const data = await response.json();
        userData = data["data"];
    }
    if (userData) {
        console.log(userData);
        showModalButton.textContent = "登出系統";
        showModalButton.addEventListener("click", () => {
            localStorage.removeItem("token");
            window.location.reload();
        });
    } else {
        showModalButton.addEventListener("click", () => {
            loginForm.style.display = "flex";
        });
    }
}





function isEmailValid(email) {
    const emailRegex = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$/;
    return emailRegex.test(email);
};







