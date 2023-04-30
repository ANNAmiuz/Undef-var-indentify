def level1():
    def level2_unused():
        def level3_used():
            i = 1+1
        def level3_unused():
            i = 2<=3
        level3_used()
    def level2_used():
        def level3_used():
            i = 1>=4
        def level3_unused():
            i = 2*4
        level3_used()
    level2_used()
level1()