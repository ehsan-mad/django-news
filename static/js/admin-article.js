(function($) {
    $(document).ready(function() {
        // Function to handle conditional display of breaking news fields
        function toggleBreakingNewsFields() {
            var isBreakingNews = $('#id_is_breaking_news').is(':checked');
            var breakingNewsFields = $('.field-breaking_news_text, .field-show_breaking_image');
            
            if (isBreakingNews) {
                breakingNewsFields.show();
            } else {
                breakingNewsFields.hide();
            }
        }
        
        // Run on page load
        toggleBreakingNewsFields();
        
        // Run on checkbox change
        $('#id_is_breaking_news').change(function() {
            toggleBreakingNewsFields();
        });
        
        // Add custom styling to make checkbox more prominent
        $('#id_show_breaking_image').parent().addClass('prominent-checkbox');
        
        // Add a descriptive label to the checkbox
        if ($('#id_show_breaking_image').length) {
            var label = $('label[for="id_show_breaking_image"]');
            if (label.length) {
                label.html('<strong>Display Image in Breaking News Banner</strong>');
            }
        }
    });
})(django.jQuery);
