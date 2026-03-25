LABS := lab1 lab2 lab3 lab4 lab5

.PHONY: all clean $(LABS)

all: $(LABS)

$(LABS):
	cd $@ && latexmk -pdf -interaction=nonstopmode main.tex

clean:
	for d in $(LABS); do cd $$d && latexmk -C && cd ..; done
