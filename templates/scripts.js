/ Smooth scrolling effect for anchor links
document.addEventListener("DOMContentLoaded", () => {
    // Sticky Nav Background Change on Scroll
    const navbar = document.querySelector(".navbar");
    window.addEventListener("scroll", () => {
      if (window.scrollY > 50) {
        navbar.classList.add("scrolled");
      } else {
        navbar.classList.remove("scrolled");
      }
    });
  
    // "Try Now" button scrolls to Features section
    const tryNowBtn = document.getElementById("tryNowBtn");
    tryNowBtn.addEventListener("click", () => {
      const featuresSection = document.getElementById("features");
      featuresSection.scrollIntoView({ behavior: "smooth" });
    });
  
    // "Learn More" button (just an example alert or link)
    const learnMoreBtn = document.getElementById("learnMoreBtn");
    learnMoreBtn.addEventListener("click", () => {
      alert("Here you can provide more details or link to a new page!");
    });
  });
  
