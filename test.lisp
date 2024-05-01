(progn
    (set 'add (lambda (a) (lambda (b) (+ a b))))
    (set 'inc (call add 1))
)
