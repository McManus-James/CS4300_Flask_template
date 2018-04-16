$(document).ready(function () {
  console.log("hello")
  $('.output').hide();
  $('#output1').show();
  $('#exercise').change(function () {
    $('.output').hide();
    $('#output'+$(this).val()).show();
  })
});