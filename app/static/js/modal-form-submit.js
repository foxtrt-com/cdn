/*!
 * Form submit function for modals
 *
 * Foxtrt.com - https://foxtrt.com
 * Copyright 2025 - Licensed under GPL-3.0
 */

const modalFormSubmit = (event, formUrl) => {
  toggleModal(event);

  fetch(formUrl + '/' + document.getElementById("modal-selected-id").value, {
    method:'POST',
  });
  location.reload(true);
};