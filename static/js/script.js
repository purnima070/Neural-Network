document.addEventListener("DOMContentLoaded", function () {

    const fileInput = document.querySelector('input[name="img"]');
    const uploadArea = document.querySelector(".upload-area");
    const uploadForm = document.querySelector(".form-box form");
    const detectButton = document.querySelector(".detect-btn");

    const previewBox = document.createElement("div");

    previewBox.className = "image-preview";

    previewBox.innerHTML = `
        <img class="preview-image" src="" alt="Selected plant image">

        <div class="preview-details">
            <strong class="preview-name"></strong>
            <span class="preview-size"></span>
        </div>

        <button type="button" class="remove-image">
            ×
        </button>
    `;

    uploadArea.parentNode.insertBefore(
        previewBox,
        uploadArea.nextSibling
    );


    fileInput.addEventListener("change", function () {

        const file = this.files[0];

        if (!file) {
            return;
        }

        validateAndPreview(file);

    });


    function validateAndPreview(file) {

        const allowedTypes = [
            "image/jpeg",
            "image/png"
        ];

        if (!allowedTypes.includes(file.type)) {

            alert("Please upload a JPG or PNG image.");

            fileInput.value = "";

            hidePreview();

            return;
        }


        const maxSize = 10 * 1024 * 1024;

        if (file.size > maxSize) {

            alert("Image size must be less than 10 MB.");

            fileInput.value = "";

            hidePreview();

            return;
        }


        const reader = new FileReader();

        reader.onload = function (event) {

            previewBox.querySelector(".preview-image").src =
                event.target.result;

            previewBox.querySelector(".preview-name").textContent =
                file.name;

            previewBox.querySelector(".preview-size").textContent =
                formatFileSize(file.size);

            previewBox.classList.add("show");

            uploadArea.classList.add("has-image");

        };

        reader.readAsDataURL(file);
    }


    function hidePreview() {

        previewBox.classList.remove("show");

        uploadArea.classList.remove("has-image");

    }


    previewBox.querySelector(".remove-image")
        .addEventListener("click", function () {

            fileInput.value = "";

            hidePreview();

        });


    function formatFileSize(bytes) {

        if (bytes < 1024) {
            return bytes + " Bytes";
        }

        if (bytes < 1024 * 1024) {
            return (bytes / 1024).toFixed(1) + " KB";
        }

        return (bytes / (1024 * 1024)).toFixed(1) + " MB";

    }


    ["dragenter", "dragover"].forEach(function (eventName) {

        uploadArea.addEventListener(eventName, function (event) {

            event.preventDefault();

            uploadArea.classList.add("dragging");

        });

    });


    ["dragleave", "drop"].forEach(function (eventName) {

        uploadArea.addEventListener(eventName, function (event) {

            event.preventDefault();

            uploadArea.classList.remove("dragging");

        });

    });


    uploadArea.addEventListener("drop", function (event) {

        const files = event.dataTransfer.files;

        if (!files.length) {
            return;
        }

        const file = files[0];

        try {

            const dataTransfer = new DataTransfer();

            dataTransfer.items.add(file);

            fileInput.files = dataTransfer.files;

        } catch (error) {

            console.log("Could not attach dropped file.");

        }

        validateAndPreview(file);

    });


    uploadForm.addEventListener("submit", function () {

        detectButton.disabled = true;

        detectButton.classList.add("analyzing");

        detectButton.innerHTML = `
            <span class="loading-content">
                <span class="spinner"></span>
                Analyzing Plant...
            </span>

            <span>⏳</span>
        `;

    });

});