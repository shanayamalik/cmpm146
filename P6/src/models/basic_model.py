from models.model import Model
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Dense, Flatten
from tensorflow.keras.optimizers import RMSprop

class BasicModel(Model):
    def _define_model(self, input_shape, categories_count):
        self.model = Sequential([
            # First Conv Block
            Conv2D(16, (3, 3), activation='relu', padding='same', input_shape=input_shape),
            MaxPooling2D(3, 3),  # Increased pool size to reduce dimensions faster
            
            # Second Conv Block
            Conv2D(24, (3, 3), activation='relu', padding='same'),
            MaxPooling2D(3, 3),  # Increased pool size
            
            # Third Conv Block
            Conv2D(32, (3, 3), activation='relu', padding='same'),
            MaxPooling2D(2, 2),
            
            # Fourth Conv Block - final reduction
            Conv2D(32, (3, 3), activation='relu', padding='same'),
            MaxPooling2D(2, 2),
            
            # Flatten and Dense layers
            Flatten(),
            Dense(24, activation='relu'),  # Reduced units
            Dense(categories_count, activation='softmax')
        ])
    
    def _compile_model(self):
        self.model.compile(
            optimizer=RMSprop(learning_rate=0.001),
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
