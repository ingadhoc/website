$(document).ready(function() {
    $('.oe_website_login_container').each(function(ev){
    	var oe_website_login_container  = this;
    	$(oe_website_login_container).on('click', 'span.input-group-btn button.btn.btn-default', function(){
    		var icon = $(this).find('i.fa.fa-eye').length
    		if ( icon == 1)
    		{
    			$(this).find('i.fa.fa-eye').removeClass('fa-eye').addClass('fa-eye-slash');
    			$(this).parent().prev('input[type="password"]').prop('type', 'text');
    		}
    		else
    		{
    			$(this).find('i.fa.fa-eye-slash').removeClass('fa-eye-slash').addClass('fa-eye');
    			$(this).parent().prev('input[type="text"]').prop('type', 'password');
    		}
    	});

    });
});