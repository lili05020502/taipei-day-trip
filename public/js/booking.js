// const token = localStorage.getItem("token");
const userName = document.getElementById("username");
const userNameInput = document.getElementById("ContactuserNameInput");
const EmailInput = document.getElementById("ContactuserEmailInput");

const NoBookingData = document.querySelector(".no-booking-data");
const BookingBox = document.querySelector(".booking-box");
const BookingContactBox = document.querySelector(".booking-contact-box");
const BookingPaymentBox = document.querySelector(".booking-payment-box");
const BookingConfirnBox = document.querySelector(".booking-confirn-box");

const bookingName = document.getElementById("booking-name");
const BookingDate = document.getElementById("booking-date");
const BookingTime = document.getElementById("booking-time");
const BookingFee = document.getElementById("booking-fee");
const BookingLocation = document.getElementById("booking-location");
const bookingImg = document.querySelector(".att-img img");
// userNameInput.value = data.data.name;
// EmailInput.value = data.data.email;
initbooking()
async function initbooking() {
    if (token == null) {
        console.log("未登入");
        window.location.href = "/";
    }
    if (token) {
        const username = document.getElementById("username");
        const response = await fetch("/api/user/auth", {
            method: "GET",
            headers: {
                Authorization: "Bearer " + token,
            },
        });
        const data = await response.json();
        // bookingData = data["data"];
        if ("error" in data) {
            console.log("error in data");
            window.location.href = "/";
        }

        // console.log("bookingData:",bookingData);
        console.log("data", data);
        username.textContent = userData["name"];
        userNameInput.value = userData["name"];
        EmailInput.value = userData["email"];
        getbooking();
        async function getbooking() {
            const response = await fetch("/api/booking", {
                method: "GET",
                headers: {
                    Authorization: "Bearer " + token,
                },
            });
            const bookingdata = await response.json();
            console.log("booking_post_res:", bookingdata);
            console.log("data[data]:", bookingdata["data"]);
            // if ("undefined"in data["data"]) {
            if (bookingdata["data"] === null) {
                console.log("沒有booking資料");
                NoBookingData.style.display = "flex";
                BookingBox.style.display = "none";
                BookingContactBox.style.display = "none";
                BookingPaymentBox.style.display = "none";
                BookingConfirnBox.style.display = "none";


                const footer = document.querySelector('footer');
                footer.style.height = '100vh';
                footer.style.alignItems = 'flex-start';
                return 0;
            }
            console.log("有資料:", bookingdata["data"])
            if (bookingdata["data"]["time"] === "morning") {
                BookingTime.textContent = "早上 ";
            } else {
                BookingTime.textContent = "下午";
            };
            const image = bookingdata["data"]["attraction"]["image"]
            console.log("image:", bookingdata["data"]["attraction"]["image"])
            bookingName.textContent = bookingdata["data"]["attraction"]["name"]
            BookingDate.textContent = bookingdata["data"]["date"]
            BookingFee.textContent = bookingdata["data"]["price"]
            BookingLocation.textContent = bookingdata["data"]["attraction"]["address"]
            bookingImg.setAttribute("src", image);

        }
    }
}

const deleteBookingBtn = document.getElementById("delete-booking-btn");


deleteBookingBtn.addEventListener("click", deletebooking);

async function deletebooking() {
    console.log("按下刪除鍵")
    if (token == null) {
        console.log("未登入");
        window.location.href = "/";
    }
    if (token) {
        const response = await fetch("/api/user/auth", {
            method: "GET",
            headers: {
                Authorization: "Bearer " + token,
            },
        });
        const data = await response.json();
        console.log("data:", data)
        if ("error" in data) {
            console.log("error in data");
            window.location.href = "/";
            return 0;
        }
        fetchdelete()
        async function fetchdelete() {
            const response = await fetch("/api/booking", {
                method: "DELETE",
                headers: {
                    Authorization: "Bearer " + token,
                },

            }); const data = await response.json();
            console.log("fetchdelete_data:", data)
            if ("ok" in data) {
                console.log("刪除成功");
                location.reload();
            }
        }
    }
}

