$(document).ready(function() {
  $('form').on('change', function(event) {
    if ($('#target').text() == "")
      $('#target').text('Аиҭагара иаҿуп')
    else
      $('#target').text($('#target').text() + "...")
    $.ajax({
        data: {
          source: $('#source').val(),
          langSrc: $('#lang-src .active').attr('data-lang'),
          langTgt: $('#lang-tgt .active').attr('data-lang')
        },
        type: 'POST',
        url: '/translate'
      })
      .done(function(data) {
        $('#target').text(data.target)
      });
    event.preventDefault();
  });
});