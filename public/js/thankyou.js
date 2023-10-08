const thankyouTitleP1 = document.getElementById("thankyou-title-p-1");
const thankyouTitleP2 = document.getElementById("thankyou-title-p-2");

const orderNumber = document.getElementById("order-number");
const orderMsg = document.getElementById("order-msg");

const queryString = window.location.search;
const urlParams = new URLSearchParams(queryString);
const orderNum = urlParams.get('number');



orderNumber.textContent = orderNum;

const orderDetail = document.querySelector(".order-detail");
const orderDetailPrice = document.getElementById("detail-price");
const orderDetailAttName = document.getElementById("detail-att-name");
const orderDetailAddress = document.getElementById("detail-att-address");
const orderDetailDate = document.getElementById("detail-date");
const orderDetailTime = document.getElementById("detail-time");
const orderPaystatus = document.getElementById("detail-pay-status");
initthankyou()

async function initthankyou() {
    if (token == null) {
        console.log("未登入");
        window.location.href = "/";
    }
    const response = await fetch(`/api/orders/${orderNum}`, {
        method: "GET",
        headers: {
            Authorization: "Bearer " + token,
        },
    });
    const orderData = await response.json();
    //   console.log(orderData);
    if (orderData == null) {
        console.log("orderData:", orderData);
        console.log("查無此訂單編號");
        thankyouTitleP1.textContent = "查無此訂單編號";
    }
    if (orderData) {
        console.log("查詢到訂單")
        console.log(orderData);
        thankyouTitleP1.textContent = "行程預定成功";
        thankyouTitleP2.textContent = "您的訂單編號如下";
        orderMsg.textContent = "請記住此編號";
        showdetail(orderData);

    }


}
function showdetail(orderData) {
    if(orderData.data.status==1){
        paystatus="已付款"
    }
    else{
        paystatus="未付款"
    }
    orderDetail.style.display = "flex";
    orderDetailPrice.textContent = orderData.data.price;
    orderDetailAttName.textContent = orderData.data.trip.attraction.name;
    orderDetailAddress.textContent = orderData.data.trip.attraction.address;
    orderDetailDate.textContent = orderData.data.trip.date;
    orderDetailTime.textContent = orderData.data.trip.time;
    orderPaystatus.textContent = paystatus;
}






















