document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements 
    const elements = {
        modal: document.getElementById('crudModal'),
        addButton: document.getElementById('addReviewBtn'),
        cancelButton: document.getElementById('cancelReview'),
        saveButton: document.getElementById('saveReview'),
        reviewForm: document.getElementById('reviewForm'),
        reviewsContainer: document.getElementById('reviewsContainer'),
        stars: document.querySelectorAll('#starRating .star'),
        ratingInput: document.getElementById('rating')
    };

    // Configuration
    const config = {
        csrfToken: document.querySelector('meta[name="csrf-token"]')?.getAttribute('content'),
        addReviewUrl: elements.addButton?.getAttribute('data-add-url') // Use URL from data attribute if present
    };

    // Review Card Generator
    const ReviewCardGenerator = {
        createStarRating(rating) {
            return '★'.repeat(rating).padEnd(5, '☆')
                .split('')
                .map(star => `<span class="star ${star === '★' ? 'text-yellow-400' : 'text-gray-300'}">${star}</span>`)
                .join('');
        },

        createActionButtons(reviewId, csrfToken) {
            return `
                <div class="flex space-x-2 mt-4">
                    <a href="/review/edit-product-review/${reviewId}/" 
                    class="bg-yellow-500 text-white px-4 py-2 rounded-lg hover:bg-yellow-600 transition-colors">
                        Edit
                    </a>
                    <form action="/review/delete/${reviewId}/" method="post" class="delete-review-form" data-delete-url="/review/delete/${reviewId}/">
                        <input type="hidden" name="csrfmiddlewaretoken" value="${csrfToken}">
                        <button type="submit" class="bg-red-500 text-white px-4 py-2 rounded-lg hover:bg-red-600 transition-colors">
                            Delete
                        </button>
                    </form>
                </div>
            `;
        },

        generateCard(review) {
            const isProductDetailsPage = document.body.classList.contains('product-details-page');
        
            if (isProductDetailsPage) {
                // Template product_details.html
                return `
                    <div class="review-card bg-white rounded-lg shadow-md p-6 mb-4">
                        <!-- Review Header -->
                        <div class="review-header flex justify-between items-center mb-2">
                            <div class="reviewer text-xl font-semibold">${review.restaurant_name}</div>
                            <div class="review-date text-gray-500 text-sm">${review.date_added}</div>
                        </div>
        
                        <!-- Food Name -->
                        <p class="text-gray-600 mb-2 font-medium">Food: ${review.food_name}</p>
        
                        <!-- Star Rating -->
                        <div class="review-rating flex space-x-1 mb-2">
                            ${this.createStarRating(review.rating)}
                        </div>
        
                        <!-- Review Text -->
                        <div class="review-text text-gray-700 mb-4">
                            ${review.review}
                        </div>
        
                        <!-- Action Buttons -->
                        <div class="flex space-x-2 mt-4">
                            <a href="/review/edit-product-review/${review.id}/" 
                               class="bg-yellow-500 text-white px-4 py-2 rounded-lg hover:bg-yellow-600 transition-colors">
                                Edit
                            </a>
                            <form action="/review/delete/${review.id}/" method="post" class="delete-review-form" data-delete-url="/review/delete/${review.id}/">
                                <input type="hidden" name="csrfmiddlewaretoken" value="${config.csrfToken}">
                                <button type="submit" class="bg-red-500 text-white px-4 py-2 rounded-lg hover:bg-red-600 transition-colors">
                                    Delete
                                </button>
                            </form>
                        </div>
                    </div>
                `;
            } else {
                // Template reviews.html
                return `
                    <div class="bg-white rounded-lg shadow-md p-6 mb-4">
                        <h3 class="text-xl font-bold mb-2">${review.restaurant_name}</h3>
                        <p class="text-gray-600 mb-2">${review.food_name}</p>
                        <div class="flex space-x-1 mb-2">
                            ${this.createStarRating(review.rating)}
                        </div>
                        <p class="text-gray-700 mb-2">${review.review}</p>
                        <p class="text-sm text-gray-500">Added on ${review.date_added}</p>
                        <div class="flex space-x-2 mt-4">
                            <a href="/review/edit-product-review/${review.id}/" 
                               class="bg-yellow-500 text-white px-4 py-2 rounded-lg hover:bg-yellow-600 transition-colors">
                                Edit
                            </a>
                            <form action="/review/delete/${review.id}/" method="post" class="delete-review-form" data-delete-url="/review/delete/${review.id}/">
                                <input type="hidden" name="csrfmiddlewaretoken" value="${config.csrfToken}">
                                <button type="submit" class="bg-red-500 text-white px-4 py-2 rounded-lg hover:bg-red-600 transition-colors">
                                    Delete
                                </button>
                            </form>
                        </div>
                    </div>
                `;
            }
        }
        
    };

    // Modal Controller 
    const ModalController = {
        show() {
            elements.modal.classList.remove('hidden');
        },
        
        hide() {
            elements.modal.classList.add('hidden');
            elements.reviewForm?.reset();
            StarRatingController.reset();
        },
        
        init() {
            if (elements.addButton && elements.modal) {
                elements.addButton.addEventListener('click', this.show);
            }
            if (elements.cancelButton && elements.modal) {
                elements.cancelButton.addEventListener('click', this.hide);
            }
        }
    };

    // Star Rating Controller 
    const StarRatingController = {
        updateStars(selectedValue) {
            elements.stars.forEach(star => {
                const value = star.dataset.value;
                star.classList.toggle('text-yellow-400', value <= selectedValue);
                star.classList.toggle('text-gray-300', value > selectedValue);
            });
        },

        reset() {
            elements.stars.forEach(star => {
                star.classList.remove('text-yellow-400');
                star.classList.add('text-gray-300');
            });
            if (elements.ratingInput) elements.ratingInput.value = '';
        },

        init() {
            if (elements.stars.length > 0) {
                elements.stars.forEach(star => {
                    star.addEventListener('click', () => {
                        const value = star.dataset.value;
                        if (elements.ratingInput) elements.ratingInput.value = value;
                        this.updateStars(value);
                    });
                });
            }
        }
    };

    // Review Submission Controller 
    const ReviewSubmissionController = {
        async submitReview(event) {
            event.preventDefault();
            
            try {
                const response = await fetch(config.addReviewUrl, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': config.csrfToken
                    },
                    body: new FormData(elements.reviewForm)
                });

                const responseData = await response.json();
                if (!response.ok) throw new Error(responseData.error || 'Failed to add review');

                this.handleSuccessfulSubmission(responseData);
            } catch (error) {
                console.error('Error:', error);
                alert(`Error adding review: ${error.message}`);
            }
        },

        handleSuccessfulSubmission(newReview) {
            const noReviewMessage = document.querySelector('.no-reviews-placeholder');
            if (noReviewMessage) noReviewMessage.remove();

            // Add new review card untuk `reviewsContainer`
            const newCardHTML = ReviewCardGenerator.generateCard(newReview);
            if (elements.reviewsContainer) {
                const newCard = document.createElement('div');
                newCard.innerHTML = newCardHTML;
                elements.reviewsContainer.prepend(newCard.firstElementChild);
            }

            // Reset form dan close modal
            ModalController.hide();
        },

        init() {
            if (elements.saveButton && elements.reviewForm) {
                elements.saveButton.addEventListener('click', this.submitReview.bind(this));
            }

            // Event delegation untuk delete forms
            if (elements.reviewsContainer) {
                elements.reviewsContainer.addEventListener('submit', async function(e) {
                    if (e.target.classList.contains('delete-review-form')) {
                        e.preventDefault();
                        const deleteUrl = e.target.getAttribute('data-delete-url');

                        console.log('Attempting to delete review with URL:', deleteUrl);


                        if (confirm('Are you sure you want to delete this review?')) {
                            try {
                                const response = await fetch(deleteUrl, {
                                    method: 'POST',
                                    headers: {
                                        'X-CSRFToken': config.csrfToken
                                    }
                                });
                                
                                if (response.ok) {
                                    e.target.closest('.bg-white').remove();
                                    if (elements.reviewsContainer.children.length === 0) {
                                        location.reload();
                                    }
                                } else {
                                    const errorData = await response.json();
                                    throw new Error(errorData.error || 'Failed to delete review');
                                }
                            } catch (error) {
                                console.error('Error:', error);
                                alert(`Error deleting review: ${error.message}`);
                            }
                        }
                    }
                });
            }
        }
    };

    if (elements.modal && elements.addButton) ModalController.init();
    if (elements.stars.length > 0) StarRatingController.init();
    if (elements.reviewForm && config.addReviewUrl) ReviewSubmissionController.init();
});