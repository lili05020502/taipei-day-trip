// const token = localStorage.getItem("token");
const userName = document.getElementById("username");
const userNameInput = document.getElementById("ContactuserNameInput");
const EmailInput = document.getElementById("ContactuserEmailInput");
const PhoneInput = document.getElementById("ContactuserPhoneInput");
const ConfrimBtn = document.getElementById("confrimBtn");

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
const BookingDollar = document.getElementById("dollar");


let attractionId;
let attractionName;
let attractionAddress;
let attractionImage;


let orderDate;
let orderTime;
let orderPrice;
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
                // BookingBox.style.display = "none";
                // BookingContactBox.style.display = "none";
                // BookingPaymentBox.style.display = "none";
                // BookingConfirnBox.style.display = "none";


                const footer = document.querySelector('footer');
                footer.style.height = '100vh';
                footer.style.alignItems = 'flex-start';
                return 0;
            }
            console.log("有資料:", bookingdata["data"])
            BookingBox.style.display = "flex";
            BookingContactBox.style.display = "flex";
            BookingPaymentBox.style.display = "flex";
            BookingConfirnBox.style.display = "flex";
            if (bookingdata["data"]["time"] === "morning") {
                BookingTime.textContent = "早上 ";
                orderTime="morning"
            } else {
                BookingTime.textContent = "下午";
                orderTime="afternoon"
            };
            const image = bookingdata["data"]["attraction"]["image"]
            console.log("image:", bookingdata["data"]["attraction"]["image"])
            attractionName=bookingName.textContent = bookingdata["data"]["attraction"]["name"]
            orderDate=BookingDate.textContent = bookingdata["data"]["date"]
            orderPrice=BookingFee.textContent = bookingdata["data"]["price"]
            attractionAddress=BookingLocation.textContent = bookingdata["data"]["attraction"]["address"]
            bookingImg.setAttribute("src", image);
            BookingDollar.textContent = bookingdata["data"]["price"]
            attractionId=bookingdata["data"]["attraction"]["id"]
            attractionImage=image
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


// -----------
//TapPay
// -----------
TPDirect.setupSDK(137070, 'app_nrQ489PKgC4gevxhCV0uEfseX0pv78FE4F5UBCkyzzG2g5dXOovctTSC6Kzp', 'sandbox')

let fields = {
    number: {
        // css selector
        element: '#card-number',
        placeholder: '**** **** **** ****'
    },
    expirationDate: {
        // DOM object
        element: document.getElementById('card-expiration-date'),
        placeholder: 'MM / YY'
    },
    ccv: {
        element: '#card-ccv',
        placeholder: 'ccv'
    }
}

TPDirect.card.setup({
    // Display ccv field



    fields: fields,
    styles: {
        // Style all elements
        'input': {
            'color': 'gray'
        },
        // Styling ccv field
        'input.ccv': {
            // 'font-size': '16px'
        },
        // Styling expiration-date field
        'input.expiration-date': {
            // 'font-size': '16px'
        },
        // Styling card-number field
        'input.card-number': {
            // 'font-size': '16px'
        },
        // style focus state
        ':focus': {
            // 'color': 'black'
        },
        // style valid state
        '.valid': {
            'color': 'green'
        },
        // style invalid state
        '.invalid': {
            'color': 'red'
        },
        // Media queries
        // Note that these apply to the iframe, not the root window.
        '@media screen and (max-width: 400px)': {
            'input': {
                'color': 'orange'
            }
        }
    },
    // 此設定會顯示卡號輸入正確後，會顯示前六後四碼信用卡卡號
    isMaskCreditCardNumber: true,
    maskCreditCardNumberRange: {
        beginIndex: 6,
        endIndex: 11
    }
})

const phonePattern = /^09[0-9]{8}$/;

ConfrimBtn.addEventListener("click",function(event){
    
    console.log("按下了確認訂購按鈕");
    if(userNameInput.value==""){
        console.log("姓名未填");
        alert("姓名未填");
        return
    }
    else if(EmailInput.value==""){
        console.log("信箱未填");
        alert("信箱未填");
        return
    }
    else if(PhoneInput.value==""){
        console.log("手機號碼未填");
        alert("手機號碼未填");
        return
    }
    else if(!isEmailValid(EmailInput.value)){
        console.log("信箱格式不正確")
        alert("信箱格式不正確");
        return
    }
    // const phonePattern = /^09[0-9]{8}$/;
    else if(!validatePhoneNumber(PhoneInput.value)){
        console.log("手機格式不正確")
        alert("手機格式不正確");
        return
    }
    
    // console.log(TPDirect.card.getTappayFieldsStatus());
    onSubmit();
    function onSubmit() {
    
        // TPDirect.card.getPrime(callback)
        // 取得 TapPay Fields 的 status
        const tappayStatus = TPDirect.card.getTappayFieldsStatus()
        console.log(tappayStatus);
        // 確認是否可以 getPrime
        if (tappayStatus.canGetPrime === false) {
            // alert('can not get prime')
            console.log('can not get prime');
            alert("信用卡資訊不正確");
            return
        }
    
        // Get prime
        TPDirect.card.getPrime((result) => {
            if (result.status !== 0) {
                // alert('get prime error ' + result.msg)
                console.log("result.status:",result.status);
                console.log("get prime error" , result.msg);
                alert("信用卡資訊不正確");
                return
            }
            // alert('get prime 成功，prime: ' + result.card.prime)
            console.log("get prime 成功，prime :",result.card.prime);
            let Data={
                "prime": result.card.prime,
                "order": {
                  "price": orderPrice,
                  "trip": {
                    "attraction": {
                      "id": attractionId,
                      "name": attractionName,
                      "address": attractionAddress,
                      "image": attractionImage
                    },
                    "date": orderDate,
                    "time": orderTime
                  },
                  "contact": {
                    "name": userNameInput.value,
                    "email": EmailInput.value,
                    "phone": PhoneInput.value
                  }
                }
            }
            console.log(Data)
            
            fetch('/api/orders', {
                method: 'POST',
                headers: { "Content-Type": "application/json",
                Authorization: "Bearer " + token, },
                body: JSON.stringify(Data)
            }).then(response => {
                return response.json();
            }).then(function (data) {
                // let cat=data
                if("data"in data){
                    if (data.data.payment.status === 0) {
                        console.log("成功");
                        console.log(data.data.number);
                        ordernumber=data.data.number;
                        // location.href = "/thankyou?number=" + data.data.number
                        // location.href = "/thankyou";
                        window.location.href = `/thankyou?number=${ordernumber}`;
                    }
                }
                else {
                    // console.log(data)
                    console.log(data.message)
                    alert(data.message)
                    //alert("伺服器內部錯誤，請再試一次");
                    // console.log("伺服器內部錯誤，請再試一次");
                }
        
            })
        

            return 
            // send prime to your server, to pay with Pay by Prime API .
            // Pay By Prime Docs: https://docs.tappaysdk.com/tutorial/zh/back.html#pay-by-prime-api
        })
    }
})




function isEmailValid(email) {
    const emailRegex = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$/;
    return emailRegex.test(email);
};

function validatePhoneNumber(phoneNumber) {
    const phonePattern = /^09[0-9]{8}$/;
    return phonePattern.test(phoneNumber);
};