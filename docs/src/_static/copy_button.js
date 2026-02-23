/* Copy button, thanks to https://chrisholdgraf.com/blog/2018/sphinx-copy-buttons/ */

function addCopyButtonToCode() {
    const codeBlocks = document.querySelectorAll("div.highlight pre");
    codeBlocks.forEach(function (codeBlock, index) {
        const currentId = "codeblock" + index;
        codeBlock.setAttribute("id", currentId);
        const copyButton = document.createElement("button");
        copyButton.className = "copy-button";
        copyButton.dataset.clipboardTarget = "#" + currentId;
        copyButton.title = "Copy to clipboard";
        const img = document.createElement("img");
        img.setAttribute("src", "_static/copy_button.svg");
        copyButton.appendChild(img);
        codeBlock.parentNode.insertBefore(copyButton, codeBlock.nextSibling);
    });

    const clipboard = new ClipboardJS(".copy-button");

    // Show "Copied!" popup on successful copy
    clipboard.on("success", function (event) {
        event.clearSelection(); // Don't show the contents of the code block as selected after copying
        const popup = document.createElement("span");
        popup.textContent = "Copied!";
        popup.className = "copy-button-popup";
        event.trigger.before(popup); // Insert the popup before the button that triggered it

        // Fade in the popup
        setTimeout(function () {
            popup.style.opacity = "1";
        }, 50); // Small delay to ensure DOM render before transition starts

        // Fade out and remove the popup after a short duration
        setTimeout(function () {
            popup.style.opacity = "0";
            setTimeout(function () {
                if (popup.parentNode) {
                    // Check if the element still exists before attempting to remove
                    popup.remove();
                }
            }, 300); // Matches transition duration in CSS for smooth removal
        }, 2000); // Popup visible for 2 seconds
    });
}

document.addEventListener("DOMContentLoaded", function () {
    addCopyButtonToCode();
});
