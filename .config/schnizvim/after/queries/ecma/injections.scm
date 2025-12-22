;; extends

; (call_expression
; 	function: (identifier) @tagged_template
; 		(#eq? @tagged_template "html")
; 	arguments: (template_string) @injection.content
; 		(#set! injection.language "html")
; 		(#set! injection.include-children)
; 		(#set! priority 200)
; )

(call_expression
  function: (identifier) @_name
  (#any-of? @_name "html")
  arguments: (template_string) @injection.content
  (#offset! @injection.content 0 1 0 -1)
  (#set! injection.include-children)
  (#set! injection.language "html"))
