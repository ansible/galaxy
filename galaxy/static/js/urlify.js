$(function() {
  // Make links from relative URLs to resources.
  $('span.str').each(function() {
    // Remove REST API links within data.
    if ($(this).parent('a').size()) {
      $(this).unwrap();
    }
    var s = $(this).html();
    if (s.match(/^\"\/.+\/\"$/) || s.match(/^\"\/.+\/\?.*\"$/)) {
      $(this).html('"<a href=' + s + '>' + s.replace(/\"/g, '') + '</a>"');
    }
  });
  // Make links for all inventory script hosts.
  $('.request-info .pln:contains("script")').each(function() {
    $('.response-info span.str:contains("hosts")').each(function() {
      if ($(this).text() != '"hosts"') {
        return;
      }
      var hosts_state = 0;
      $(this).find('~ span').each(function() {
          if (hosts_state == 0) {
            if ($(this).is('span.pun') && $(this).text() == '[') {
              hosts_state = 1;
            }
          }
          else if (hosts_state == 1) {
            if ($(this).is('span.pun') && ($(this).text() == ']' || $(this).text() == '],')) {
              hosts_state = 2;
            }
            else if ($(this).is('span.str')) {
              if ($(this).text() == '"') {
              }
              else if ($(this).text().match(/^\".+\"$/)) {
                var s = $(this).text().replace(/\"/g, '');
                $(this).html('"<a href="' + '?host=' + s + '">' + s + '</a>"');
              }
              else {
                var s = $(this).text();
                $(this).html('<a href="' + '?host=' + s + '">' + s + '</a>');
              }
            }
          }
      });
    });
  });
  // Add classes/icons for dynamically showing/hiding help.
  if ($('.description').html()) {
    $('.description').addClass('well').addClass('well-small').addClass('prettyprint');
    $('.description').prepend('<a class="hide-description pull-right" href="#" title="Hide Description"><i class="icon-remove"></i></a>');
    $('a.hide-description').click(function() {
      $('.description').slideUp('fast');
      return false;
    });
    $('.page-header h1').append('<a class="toggle-description" href="#" title="Show/Hide Description"><i class="icon-question-sign"></i></a>');
    $('a.toggle-description').click(function() {
      $('.description').slideToggle('fast');
      return false;
    });
    if (window.location.hash == '#showhelp') {
      $('.description').slideDown('fast');
    }
  }
  $('.btn-primary').removeClass('btn-primary').addClass('btn-success');
});

