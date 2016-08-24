$(document).ready(function() 
{
    $('body').prepend('<a href="#" class="back-to-top">Back to Top</a>');
    var amountScrolled = 300;

    $(window).scroll(function() {
        if ($(window).scrollTop() > amountScrolled) {
            $('a.back-to-top').fadeIn('slow');
        } else {
            $('a.back-to-top').fadeOut('slow');
        }

        var scrollTop = $(window).scrollTop();
        var docHeight = $(document).height();
        var winHeight = $(window).height();
        var scrollPercent = (scrollTop) / (docHeight - winHeight);
        var scrollPercentRounded = Math.round(scrollPercent*100);
        $('a.back-to-top').text(scrollPercentRounded+"%");
    });

    $('a.back-to-top').click(function() {
        $('body,html').animate({
            scrollTop: 0
        }, 'fast');
        return false;
    });
});