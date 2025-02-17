from models.model import Model
from tensorflow.keras import Sequential, layers
from tensorflow.keras.optimizers import Adam

class BasicModel(Model):
    def _define_model(self, input_shape, categories_count):
        self.model = Sequential([
            layers.Rescaling(1./255, input_shape=input_shape),

            # First block
            layers.Conv2D(24, (3, 3), activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.MaxPooling2D((4, 4)),  # Increased pooling to reduce dimensions faster
            layers.Dropout(0.1),

            # Second block
            layers.Conv2D(32, (3, 3), activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.MaxPooling2D((3, 3)),
            layers.Dropout(0.2),

            # Third block
            layers.Conv2D(48, (3, 3), activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 2)),
            layers.Dropout(0.3),

            layers.Flatten(),
            layers.Dense(64, activation='relu'),
            layers.Dropout(0.4),
            layers.Dense(categories_count, activation='softmax')
        ])

    def _compile_model(self):
        self.model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
