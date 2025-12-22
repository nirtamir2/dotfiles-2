local function talking()
  return string.upper(vim.env.SCHNIZ_PROFILE or "") == "TALKING"
end

return {
  talking = talking,
}
