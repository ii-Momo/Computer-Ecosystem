;all tokens to use :wink:
start:
    MOV_RI R1, 10                 ; 01 01 00 00 0A 00 00 00
    MOV_RI R2, 3                  ; 01 02 00 00 03 00 00 00
    ADD   R3, R1, R2              ; 10 03 01 02 00 00 00 00
    STORE8_ABS 0x0100, R3         ; 21 00 03 00 00 01 00 00
    LOAD8_ABS  R4, 0x0100         ; 20 04 00 00 00 01 00 00
    SUB   R5, R4, R3              ; 11 05 04 03 00 00 00 00
    JZ_ABS jmp1                   ; 32 00 00 00 40 00 00 00
    MOV_RI R0, 123  ;(skipped)      01 00 00 00 7B 00 00 00
jmp1:
    MOV_RR R6, R5                 ; 02 06 05 00 00 00 00 00
    JZ_REL 16  ;(to 0x0058)         33 00 00 00 10 00 00 00
    MOV_RI R0, 77   ;(skipped)      01 00 00 00 4D 00 00 00
    JMP_REL 16 ;(to 0x0068)         31 00 00 00 10 00 00 00
    MOV_RI R0, 88   ;(skipped)      01 00 00 00 58 00 00 00
    JMP_ABS jmp2                  ; 30 00 00 00 78 00 00 00
    MOV_RI R0, 99   ;(skipped)      01 00 00 00 63 00 00 00
jmp2:
    HALT                          ; 00 00 00 00 00 00 00 00
