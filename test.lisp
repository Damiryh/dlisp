(progn
    (set 'range (lambda (a b)
        (cond
            ((= a b) NIL)
            (T (cons a (range (+ a 1) b))))))


    (set 'lst (print (range 0 150)))

    (set 'lst1 (reduce
        (lambda (item1 item2) (+ item1 item2))
        0
        lst
    ))

    (print lst1)

    (exit 0)
)
