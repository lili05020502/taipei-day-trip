// debugger;


// ----------------------------------------------
async function searchAttractionsByKeyword(keyword) {
    // 透過關鍵字搜尋景點
    const attResponse = await fetch(`/api/attractions?page=0&keyword=${keyword}`);
    const attSearchJson = await attResponse.json();

    // 如果沒有結果
    if (attSearchJson.data.length === 0) {
        removeattractions();
        const attractionsContainer = document.querySelector(".attractions");
        const noResult = document.createElement("div");
        noResult.classList.add("no-result");
        const text = document.createElement("p");
        text.textContent = "沒有結果";
        noResult.appendChild(text);
        attractionsContainer.appendChild(noResult);
    } else {
        data = attSearchJson;
        removeattractions();
        createAttractionContainer(attSearchJson);
    }
}

// ----------------------------------------------
function listenmrtlist() {
    mrtnamecontainer.forEach((mrt) => {
        const attraction = mrt.textContent;
        const input = document.querySelector("#search-input");
        mrt.addEventListener("click", async () => {
            input.value = attraction;
            console.log(`${attraction}`);
            const response = await fetch(
                `/api/attractions?page=0&keyword=${attraction}`
            );
            const data = await response.json();
            removeattractions();
            createAttractionContainer(data);
        });
    });
}


// ---------------------捷運站上下頁功能
const leftArrow = document.querySelector(".left-arrow");
const rightArrow = document.querySelector(".right-arrow");
const mrtList = document.querySelector(".mrt-list");

//取得每一頁寬度
const pageWidth = mrtList.clientWidth;
// 滾動到下一頁
function scrollToNextPage() {
    // 計算下一頁位置
    const nextScrollLeft = mrtList.scrollLeft + pageWidth - 50;
    // 設定滾動位置
    mrtList.scrollLeft = nextScrollLeft;
}
// 滾動到上一頁
function scrollToPreviousPage() {
    // 計算上一頁的位置
    const previousScrollLeft = mrtList.scrollLeft - pageWidth;
    // 设置滚动位置
    mrtList.scrollLeft = previousScrollLeft;
}
// 監聽右箭頭事件
rightArrow.addEventListener("click", scrollToNextPage);
// 監聽左箭頭事件
leftArrow.addEventListener("click", scrollToPreviousPage);

// // -----------------------------------------------
async function next_page_Loading(nextPage, keyword = null) {
    console.log(`next_page_Loading_keyword = ${keyword}`);
    console.log("loading的keyword:", keyword)
    if (keyword) {
        const response = await fetch(
            `/api/attractions?page=${nextPage}&keyword=${keyword}`
        );
        const data = await response.json();
        createAttractionContainer(data);
    } else {
        const response = await fetch(
            `/api/attractions?page=${nextPage}`
        );
        const data = await response.json();
        createAttractionContainer(data);
    }
}

function observeListItem(nextPage, keyword) {
    const attraction = document.querySelectorAll(".attraction");
    const observer = new IntersectionObserver((entries) => {
        let observed = entries[0].isIntersecting;
        console.log(`NextPage = ${nextPage}, keyword = ${keyword}`);
        if (observed) {
            observer.unobserve(entries[0].target);
            if (nextPage) {
                next_page_Loading(nextPage, keyword);
            } else {
                // console.log("沒了");
            }
        }
    });
    observer.observe(attraction[attraction.length - 1]);
}

// 第一次進入網頁fetch資料
async function fetchData() {

    const attresponse = await fetch("/api/attractions?page=0");
    const data = await attresponse.json();

    // console.log(data.nextPage);
    createAttractionContainer(data);
    // observer.observe(footer);
    fetch("/api/mrts")
        .then(response => response.json())
        .then(data => {
            // 獲取MRT站點資料
            const mrtStations = data.data;
            // console.log("mrtStations:",mrtStations)
            // 獲取mrtlist元素
            const mrtListElement = document.querySelector(".mrt-list");
            // 清空mrtlist
            mrtListElement.innerHTML = "";
            // 將資料加入mrtlist中
            mrtStations.forEach(station => {
                // console.log(station);
                const stationElement = document.createElement("div");
                stationElement.className = "mrt-container";
                stationElement.textContent = station;
                mrtListElement.appendChild(stationElement);
            });
            mrtnamecontainer = document.querySelectorAll(".mrt-list div");
            listenmrtlist();
        })
        .catch(error => {
            console.error("發生錯誤：", error);
        });
};

// -----------------------------------------------------------------------------
const searchbtn = document.querySelector(".search-btn")
searchbtn.addEventListener("click", async () => {
    const searchinput = document.querySelector("#search-input")
    const keyword = searchinput.value;
    // console.log("search-input:", ` keyword=${keyword}`);
    console.log("search之前的-keywoed", keyword);
    let attSearchResponse = await fetch(
        `/api/attractions?page=0&keyword=${keyword}`
    );
    let attsearchjson = await attSearchResponse.json();
    console.log(attsearchjson);
    if (attsearchjson.data.length === 0) {
        removeattractions();
        console.log("attsearchjson是空的");
        const attractionsContainer = document.querySelector(".attractions");
        const noResult = document.createElement("div");
        noResult.classList.add("no-result");
        const text = document.createElement("p");
        text.textContent = "沒有結果";
        noResult.appendChild(text);
        attractionsContainer.appendChild(noResult);
    }
    else {
        data = attsearchjson;
        console.log("search-data:", data);
        // console.log("有資料", data);
        // console.log("data.nextPage:",data.nextPage)
        console.log("search-keywoed", keyword);
        removeattractions();
        createAttractionContainer(data, keyword);
    }
});


// ------------------------------------------------------------------------------
function removeattractions() {
    const oldattractionsContainer = document.querySelector(".attractions-container");
    oldattractionsContainer.innerHTML = ""; // 清空 div 内的所有内容
    const attractionsContainer = document.createElement("div");
    attractionsContainer.classList.add("attractions")
    oldattractionsContainer.appendChild(attractionsContainer);
};
// ------------------------------------------------------------------------------
// 創建景點容器並加入資料
function createAttractionContainer(data, keyword) {
    console.log(data.data);
    console.log("attsearchjson:", data);
    console.log("創建景點容器keyword:", keyword);
    if (!data) {
        return;
    }
    console.log(data.nextPage);
    let attnextpage = data.nextPage;
    const attractionsArray = Array.isArray(data) ? data : data.data;
    const attractionsContainer = document.querySelector(".attractions");
    attractionsArray.forEach((attraction) => {
        const attractionElement = document.createElement("div");
        attractionElement.classList.add("attraction");
        attractionElement.setAttribute("data-id", `${attraction.id}`);
        // --
        const atag = document.createElement("a");
        atag.setAttribute("href", `/attraction/${attraction.id}`);
        console.log(`/attraction/${attraction.id}`);
        const imageAndNameDiv = document.createElement("div");
        imageAndNameDiv.classList.add("att-img");
        imageAndNameDiv.innerHTML = `
            <img src="${attraction.images[0]}" alt="${attraction.name}">
            <p>${attraction.name}</p>
        `;
        const mrtAndCategoryDiv = document.createElement("div");
        mrtAndCategoryDiv.classList.add("att-detail");
        mrtAndCategoryDiv.innerHTML = `
            <p>${attraction.mrt || ""}</p> 
            <p>${attraction.category}</p>
        `;
        attractionElement.appendChild(atag);
        attractionElement.appendChild(imageAndNameDiv);
        attractionElement.appendChild(mrtAndCategoryDiv);
        attractionsContainer.appendChild(attractionElement);

    });
    console.log(`make Attractions: keyword = ${keyword}`);
    observeListItem(attnextpage, keyword);

    document.querySelectorAll(".attraction").forEach((element) => {
        element.addEventListener("click", function () {
            const attractionId = this.getAttribute("data-id");
            const detailPageUrl = `/attraction/${attractionId}`;
            window.location.href = detailPageUrl;
        });
    });
}



window.addEventListener("load", async () => {
    fetchData();
});


