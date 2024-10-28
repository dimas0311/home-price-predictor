import React, { useState, useEffect } from "react";
import { ArrowUp } from "lucide-react";

const ScrollToTopButton = () => {
  const [isVisible, setIsVisible] = useState(false);

  // Show button when page is scrolled up to given distance
  const toggleVisibility = () => {
    if (window.scrollY > 300) {
      setIsVisible(true);
    } else {
      setIsVisible(false);
    }
  };

  // Scroll to top smoothly
  const scrollToTop = () => {
    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  };

  useEffect(() => {
    window.addEventListener("scroll", toggleVisibility);
    return () => {
      window.removeEventListener("scroll", toggleVisibility);
    };
  }, []);

  return (
    <>
      {isVisible && (
        <div
          onClick={scrollToTop}
          className="fixed bottom-4 right-1 p-4 bg-green-500 hover:bg-green-600 
                     text-black rounded-full shadow-md cursor-pointer 
                     transition-all duration-300 transform hover:scale-110
                     flex items-center justify-center z-50"
        >
          <ArrowUp size={24} strokeWidth={2.5} />
        </div>
      )}
    </>
  );
};

export default ScrollToTopButton;
