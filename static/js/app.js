console.log("Sihirli Kabin Aktif");

const cards = document.querySelectorAll(".product-card");

cards.forEach(card => {

    card.addEventListener("click", () => {

        card.style.transform = "scale(0.97)";

        setTimeout(() => {
            card.style.transform = "scale(1)";
        }, 150);

    });

});

const captureBtn = document.querySelector(".capture-btn");

if(captureBtn){

    captureBtn.addEventListener("click", () => {

        captureBtn.classList.add("flash");

        setTimeout(() => {
            captureBtn.classList.remove("flash");
        }, 300);

    });

}