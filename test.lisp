(progn
    (set 'a 2)
    (set 'b 3)
    (cond
        ((< a b) (print a))
        (T (print b))
    )
    (exit 0)
)
