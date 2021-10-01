CREATE TABLE rr_l (
    id INT NOT NULL,
    marker_id SMALLINT NOT NULL,
    packet_type_id SMALLINT NOT NULL,
    sequence_number INT NOT NULL,
    device_id INT NOT NULL,
    anchors VARCHAR(250),
    created_at timestamp NOT NULL,
    moving VARCHAR(250)
);

ALTER TABLE rr_l
  ADD CONSTRAINT "FK_rr_l_marker_id" FOREIGN KEY (marker_id) REFERENCES marker (id)
ON UPDATE NO ACTION ON DELETE NO ACTION;

ALTER TABLE rr_l
  ADD CONSTRAINT "FK_rr_l_packet_type_id" FOREIGN KEY (packet_type_id) REFERENCES packet_type (id)
ON UPDATE NO ACTION ON DELETE NO ACTION;