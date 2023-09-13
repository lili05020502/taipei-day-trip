const pathname = window.location.pathname;
const attractionId = pathname.split('/').pop(); // 假設 URL 格式為 /attraction/{attractionId}
const apiUrl = `/api/attraction/${attractionId}`;
console.log(apiUrl);
//這段沒有處理意外的景點id
// fetch(apiUrl)
//     .then((response) => response.json())
//     .then((data) => {
//         console.log(data);
//         // 在這裡處理從 API 返回的景點資訊（data），並將其顯示在網頁上
//         // displayAttractionInfo(data);
//     })
//     .catch((error) => {
//         console.error('取得景點資訊時發生錯誤：', error);
//     });
//------------------------------------------
//以下這段處理意外的景點id
// fetch(apiUrl)
//   .then(response => {
//     if (!response.ok) {
//       // 如果 API 返回錯誤，將網頁重新導回首頁或其他頁面
//       window.location.href = '/';
//       throw new Error('API 錯誤');
//     }
//     return response.json();
//   })
//   .then(data => {
//     // 在這裡處理 API 正確返回的數據
//     // 在這裡處理從 API 返回的景點資訊（data），並將其顯示在網頁上
//     // displayAttractionInfo(data);
//     console.log(data);
//   })
//   .catch(error => {
//     // 在這裡處理錯誤，例如輸出錯誤信息到控制台
//     console.error(error);
//   });
//------------------------------------------
const attractionName = document.querySelector(".order-container-h2");
const catName = document.querySelector(".category");
const mrtName = document.querySelector(".mrt");
const attImg = document.querySelector(".img img");
const attDescription = document.querySelector(".att-description-p");
const attAddress = document.querySelector(".att-address");
const attTracsport = document.querySelector(".att-transport");
const leftArrow = document.querySelector(".img-left-arrow");
const rightArrow = document.querySelector(".img-right-arrow");

let currentImageIndex = 0;
async function fetchAttracionData() {
    const response = await fetch(apiUrl);
    const data = await response.json();
    if (!response.ok) {
        // 如果 API 返回錯誤，將網頁重新導回首頁
        window.location.href = '/';
        throw new Error('API 錯誤');
    }
    console.log(data);
    console.log(data.data);
    console.log(data.data.name);
    const { name, category, address, mrt, transport, images, description } =
        data.data;
    attractionName.textContent = name;
    catName.textContent = category;
    mrtName.textContent = mrt;
    attImg.setAttribute("src", images[0]);
    attDescription.textContent = description;
    attAddress.textContent = address;
    attTracsport.textContent = transport;
    const imageCount = images.length;
    // imageCount = images.length;
    console.log("imageCount:", imageCount);
    creatimgdot(imageCount);



    function prevImage() {
        currentImageIndex--;
        if (currentImageIndex < 0) {
            currentImageIndex = imageCount - 1;
        };
        showImage(currentImageIndex);

    }
    function nextImage() {
        currentImageIndex++;
        if (currentImageIndex > imageCount - 1) {
            currentImageIndex = 0;
        };
        showImage(currentImageIndex)
    }
    function showImage() {
        console.log("showImage_currentImageIndex", currentImageIndex)
        attImg.setAttribute("src", images[currentImageIndex]);
        updateImageDot(currentImageIndex);
    }
    leftArrow.addEventListener("click", prevImage);
    rightArrow.addEventListener("click", nextImage);

};
// --------------------------------
const inputMorning = document.querySelector("#morning");
const inputafternoon = document.querySelector("#afternoon");
let cost = document.querySelector("#cost");
inputMorning.addEventListener("change", () => {
    cost.textContent = "2000";
});
inputafternoon.addEventListener("change", () => {
    cost.textContent = "2500";
});
// --------------------------------



function creatimgdot(imageCount) {
    console.log("creatimgdot-count:", imageCount);
    const dotContainer = document.querySelector(".img-dot");
    for (let i = 0; i < imageCount; i++) {
        const dot = document.createElement('div');
        dot.classList.add('dot');
        dotContainer.appendChild(dot);
    }
    console.log("creatimgdot_currentImageIndex", currentImageIndex)
    updateImageDot(currentImageIndex);

};
function updateImageDot(index) {
    const dots = document.querySelectorAll(".dot");
    dots.forEach((dot, i) => {
        if (i === index) {
            dot.classList.add("active");
        } else {
            dot.classList.remove("active");
        }
    });
}

window.addEventListener("load", async () => {
    fetchAttracionData();
});