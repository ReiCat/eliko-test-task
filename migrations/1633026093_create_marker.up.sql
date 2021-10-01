CREATE TABLE marker
(
  id smallint NOT NULL,
  name character varying(10) NOT NULL,
  CONSTRAINT "PK_marker" PRIMARY KEY (id)
)
WITH (
OIDS=FALSE
);

INSERT INTO marker VALUES(1, '$PEKIO');