$(document).ready(function() {
  $('#swap-lang').on('click', function(event) {
    src = $('#lang-src .active').data('lang');
    tgt = $('#lang-tgt .active').data('lang');
    $('#lang-src .active').removeClass("active");
    $('#lang-tgt .active').removeClass("active");
    $('#lang-src').find("[data-lang='" + tgt + "']").addClass("active");
    $('#lang-tgt').find("[data-lang='" + src + "']").addClass("active");
    if ($('#target').text() != "Аиҭагара") {
      temp = $('#source').val()
      $('#source').val($('#target').text())
      $('#target').text(temp)
      event.preventDefault();
    }
  });

  $('#translate').on('click', function(event) {
    if ($('#target').text() == "Аиҭагара" && $('#source').val() != "")
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
          langSrc: $('#lang-src .active').data('lang'),
          langTgt: $('#lang-tgt .active').data('lang')
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