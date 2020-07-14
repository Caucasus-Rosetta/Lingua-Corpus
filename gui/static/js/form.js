$(document).ready(function() {
  $('#source').on('keyup keypress', function() {
    $(this).height(0);
    $(this).height(this.scrollHeight);
  });
  $('.lang').on('click', function(event) {
    // TODO expand the behavior scope once more language pairs are available.
    // Currently works as the swap, because we only have one language pair.
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
    }
    // Support mobile
    src = $('#lang-src .active').data('lang');
    tgt = $('#lang-tgt .active').data('lang');
    src_text = $('#lang-src .active').text();
    tgt_text = $('#lang-tgt .active').text();
    $('#lang-src-sm .lang').data(src);
    $('#lang-tgt-sm .lang').data(tgt);
    $('#lang-src-sm .lang').text(src_text);
    $('#lang-tgt-sm .lang').text(tgt_text);
    event.preventDefault();
  });

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
    }
    // Support mobile
    src = $('#lang-src .active').data('lang');
    tgt = $('#lang-tgt .active').data('lang');
    src_text = $('#lang-src .active').text();
    tgt_text = $('#lang-tgt .active').text();
    $('#lang-src-sm .lang').data(src);
    $('#lang-tgt-sm .lang').data(tgt);
    $('#lang-src-sm .lang').text(src_text);
    $('#lang-tgt-sm .lang').text(tgt_text);
    event.preventDefault();
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