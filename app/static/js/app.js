function removeFormErrors($wrapper) {
  $wrapper.find('.js-field-error').remove();
  $wrapper.find('.form-group').removeClass('has-error');
}

function clearForm($wrapper) {
  removeFormErrors($wrapper);
  $wrapper.find('input').iCheck('uncheck');
  $wrapper[0].reset();
}

function mapErrorsToForm($wrapper, errorData) {
  removeFormErrors($wrapper)

  errorData.detail.forEach(function(er) {
    let errorMessage = er.msg;

    if (er.loc.length === 2) {
      let fieldName = er.loc[1];

      let $field = $wrapper.find('input[name="' + fieldName + '"]');
      let $wrapperEl = $field.closest('.form-group');
      let $error = $('<span class="js-field-error help-block"></span>');
      $error.html(errorMessage);
      $wrapperEl.append($error);
      $wrapperEl.addClass('has-error');
    }
    if (er.loc.length === 1) {
      let $error = $('<span class="js-field-error help-block" style="color: #dd4b39;"></span>');
      $error.html(errorMessage);
      $wrapper.prepend($error);
    }
  });
}
