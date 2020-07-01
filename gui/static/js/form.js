$(document).ready(function() {
  $('#swap-lang').on('click', function(event) {
    src = $('#lang-src .active').attr('data-lang')
    tgt = $('#lang-tgt .active').attr('data-lang')
    src_list = $('#lang-src .nav-link').attr('data-lang')
    tgt_list = $('#lang-tgt .nav-link').attr('data-lang')
    event.preventDefault();
  });

  $('#translate').on('click', function(event) {
    if ($('#target').text() == "Аиҭагара")
      $('#target').text('Аиҭагара иаҿуп')
    else if ($('#source').val() == "") {
      $('#target').text('Аиҭагара')
      return
    } else if ($('#target').text().slice(-3) == "...") {
      return
    } else
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