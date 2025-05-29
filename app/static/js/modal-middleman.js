/*!
 * Modal Middleman function to set selected Ids
 *
 * Foxtrt.com - https://foxtrt.com
 * Copyright 2025 - Licensed under GPL-3.0
 */

const modalMiddleman = (event, id) => {
  var modalIdElem = document.getElementById("modal-selected-id");
  modalIdElem.innerHTML = id;
  modalIdElem.value = id;

  toggleModal(event)
};